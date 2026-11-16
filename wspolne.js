/* Gabinet – część wspólna wszystkich modułów (strona główna, Kalendarz, Opisy NFZ, Opisy prywatne).
   - Sejf: użytkownicy z własnym hasłem; każdy ma losowy klucz danych AES-GCM 256, zapisany tylko w postaci zaszyfrowanej
     kluczem z hasła (PBKDF2-SHA-256) i osobno kluczem z kodu odzyskiwania. Rekordy szyfrowane osobno (losowy IV,
     nazwa rekordu jako dane uwierzytelniające). Nic nie jest wysyłane poza przeglądarkę.
   - Sesja: klucz jako niewyciągalny CryptoKey w IndexedDB „gabinet-sesja” z czasem ostatniej aktywności; po bezczynności
     strona przechodzi do logowania (dane znikają z pamięci).
   - Pasek modułów, magazyn użytkownika (IndexedDB „gabinet@<id>”), szkice formularzy, sumy dzienne wizyt, gabinety z Kalendarza,
     przeniesienie danych z poprzednich wersji (jawnych) do przestrzeni pierwszego użytkownika. */
(function () {
  'use strict';
  const TE = new TextEncoder(), TD = new TextDecoder();
  const K_USERS = 'gabinet.users', K_CUR = 'gabinet.cur', K_PREFS = 'gabinet.prefs.';
  const SESS_DB = 'gabinet-sesja', ITER = 600000, LOCK_DEF = 15;
  const MODS = [
    { id: 'kalendarz', name: 'Kalendarz', href: 'kalendarz.html' },
    { id: 'nfz', name: 'Opisy NFZ', href: 'nfz.html' },
    { id: 'prywatne', name: 'Opisy prywatne', href: 'prywatne.html' }];
  const G = window.G = { MODS, user: null, key: null, mod: null, ITER };

  /* ---------- pomocnicze ---------- */
  const rnd = n => crypto.getRandomValues(new Uint8Array(n));
  function b64(u8) { let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000)); return btoa(s); }
  function unb64(s) { const b = atob(s), u = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return u; }
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  G.esc = esc;
  function lsGet(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } }
  function lsSet(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } }
  function lsDel(k) { try { localStorage.removeItem(k); } catch (e) { } }
  function idbReq(r) { return new Promise((res, rej) => { r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error); }); }
  function idbOpen(name, stores, ver) {
    return new Promise((res, rej) => {
      let rq; try { rq = indexedDB.open(name, ver || 1); } catch (e) { rej(e); return; }
      const to = setTimeout(() => rej(new Error('baza danych przeglądarki nie odpowiada')), 6000);   // „wisząca” baza nie blokuje aplikacji
      rq.onupgradeneeded = () => { const db = rq.result; stores.forEach(s => { if (!db.objectStoreNames.contains(s)) db.createObjectStore(s); }); };
      rq.onsuccess = () => { clearTimeout(to); const db = rq.result; db.onversionchange = () => { try { db.close(); } catch (e) { } }; res(db); };
      rq.onerror = () => { clearTimeout(to); rej(rq.error || new Error('baza niedostępna')); };
      rq.onblocked = () => { clearTimeout(to); rej(new Error('baza zablokowana przez inną kartę')); };
    });
  }
  /* transakcja: obietnica spełnia się po zakończeniu; jeśli fn zwróci żądanie IDB – wynikiem jest jego wartość */
  function run(db, stores, mode, fn) {
    return new Promise((res, rej) => {
      let t; try { t = db.transaction(stores, mode); } catch (e) { rej(e); return; }
      let r; t.oncomplete = () => res(r && typeof r === 'object' && 'readyState' in r ? r.result : r);
      t.onabort = t.onerror = () => rej(t.error || new Error('zapis przerwany'));
      try { r = fn(t); } catch (e) { try { t.abort(); } catch (_) { } rej(e); }
    });
  }

  /* ---------- klucze ---------- */
  async function kekFrom(secret, salt, iter) {
    const base = await crypto.subtle.importKey('raw', TE.encode(String(secret).normalize('NFC')), 'PBKDF2', false, ['deriveKey']);
    return crypto.subtle.deriveKey({ name: 'PBKDF2', salt, iterations: iter, hash: 'SHA-256' }, base, { name: 'AES-GCM', length: 256 }, false, ['wrapKey', 'unwrapKey']);
  }
  async function wrap(dek, kek) { const iv = rnd(12); const ct = await crypto.subtle.wrapKey('raw', dek, kek, { name: 'AES-GCM', iv }); return { iv: b64(iv), ct: b64(new Uint8Array(ct)) }; }
  function unwrap(w, kek, extractable) { return crypto.subtle.unwrapKey('raw', unb64(w.ct), kek, { name: 'AES-GCM', iv: unb64(w.iv) }, { name: 'AES-GCM', length: 256 }, !!extractable, ['encrypt', 'decrypt']); }
  const B32 = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';
  function newCode() { const b = rnd(15); let bits = 0, val = 0, s = ''; for (const x of b) { val = (val << 8) | x; bits += 8; while (bits >= 5) { s += B32[(val >>> (bits - 5)) & 31]; bits -= 5; } } return s.match(/.{4}/g).join('-'); }
  function normCode(c) { return String(c || '').toUpperCase().replace(/O/g, '0').replace(/[IL]/g, '1').replace(/[^0-9A-Z]/g, ''); }
  G.normCode = normCode;

  /* ---------- szyfrowanie rekordów ---------- */
  async function enc(obj, aad, key) {
    const iv = rnd(12);
    const ct = await crypto.subtle.encrypt({ name: 'AES-GCM', iv, additionalData: TE.encode(aad) }, key || G.key, TE.encode(JSON.stringify(obj === undefined ? null : obj)));
    return 'v1:' + b64(iv) + ':' + b64(new Uint8Array(ct));
  }
  async function dec(s, aad, key) {
    if (typeof s !== 'string' || s.slice(0, 3) !== 'v1:') throw new Error('nieznany zapis');
    const p = s.split(':');
    const pt = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: unb64(p[1]), additionalData: TE.encode(aad) }, key || G.key, unb64(p[2]));
    return JSON.parse(TD.decode(pt));
  }
  G.enc = enc; G.dec = dec;
  G.isEnc = s => typeof s === 'string' && s.slice(0, 3) === 'v1:';

  /* ---------- użytkownicy ---------- */
  G.users = () => { const a = lsGet(K_USERS, []); return Array.isArray(a) ? a.filter(u => u && u.id && u.pwd && u.rec) : []; };
  const saveUsers = a => { if (!lsSet(K_USERS, a)) throw new Error('nie udało się zapisać listy użytkowników'); };
  G.hint = () => { try { return localStorage.getItem(K_CUR) || ''; } catch (e) { return ''; } };
  const setHint = id => { try { localStorage.setItem(K_CUR, id); } catch (e) { } };
  G.prefs = (uid) => Object.assign({ lockMin: LOCK_DEF }, lsGet(K_PREFS + (uid || (G.user && G.user.id) || G.hint()), {}));
  G.setPrefs = (p) => lsSet(K_PREFS + G.user.id, Object.assign(G.prefs(), p));
  function checkPwd(p) { if (typeof p !== 'string' || p.length < 6) throw new Error('Hasło musi mieć co najmniej 6 znaków.'); }

  G.createUser = async function (name, pwd) {
    name = String(name || '').trim().replace(/\s+/g, ' ').slice(0, 40); checkPwd(pwd);
    if (!name) throw new Error('Podaj imię lub nazwę użytkownika.');
    const us = G.users(); if (us.some(u => u.name.toLowerCase() === name.toLowerCase())) throw new Error('Taki użytkownik już istnieje.');
    const dek = await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, ['encrypt', 'decrypt']);
    const salt = rnd(16), rsalt = rnd(16), code = newCode(), iter = G.ITER;
    const pw = await wrap(dek, await kekFrom(pwd, salt, iter)), rc = await wrap(dek, await kekFrom(normCode(code), rsalt, iter));
    const u = { id: 'u' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6), name, created: new Date().toISOString(),
      kdf: { salt: b64(salt), iter }, pwd: pw, rec: { salt: b64(rsalt), iter, iv: rc.iv, ct: rc.ct } };
    us.push(u); saveUsers(us);
    const key = await crypto.subtle.importKey('raw', await crypto.subtle.exportKey('raw', dek), { name: 'AES-GCM', length: 256 }, false, ['encrypt', 'decrypt']);
    await sessStart(u.id, key);
    return { user: { id: u.id, name: u.name }, code };
  };
  G.login = async function (id, pwd) {
    const u = G.users().find(x => x.id === id); if (!u) throw new Error('Nie ma takiego użytkownika.');
    let key; try { key = await unwrap(u.pwd, await kekFrom(pwd, unb64(u.kdf.salt), u.kdf.iter), false); } catch (e) { throw new Error('Nieprawidłowe hasło.'); }
    await sessStart(u.id, key); return { id: u.id, name: u.name };
  };
  async function rewrapPwd(u, dek, pwd) { const salt = rnd(16); u.kdf = { salt: b64(salt), iter: G.ITER }; u.pwd = await wrap(dek, await kekFrom(pwd, salt, G.ITER)); }
  G.recover = async function (id, code, newPwd) {
    checkPwd(newPwd);
    const us = G.users(), u = us.find(x => x.id === id); if (!u) throw new Error('Nie ma takiego użytkownika.');
    let dek; try { dek = await unwrap(u.rec, await kekFrom(normCode(code), unb64(u.rec.salt), u.rec.iter), true); } catch (e) { throw new Error('Nieprawidłowy kod odzyskiwania.'); }
    await rewrapPwd(u, dek, newPwd); saveUsers(us);
    return G.login(id, newPwd);
  };
  G.changePassword = async function (oldPwd, newPwd) {
    checkPwd(newPwd);
    const us = G.users(), u = us.find(x => x.id === G.user.id);
    let dek; try { dek = await unwrap(u.pwd, await kekFrom(oldPwd, unb64(u.kdf.salt), u.kdf.iter), true); } catch (e) { throw new Error('Obecne hasło jest nieprawidłowe.'); }
    await rewrapPwd(u, dek, newPwd); saveUsers(us); return true;
  };
  G.newRecoveryCode = async function (pwd) {
    const us = G.users(), u = us.find(x => x.id === G.user.id);
    let dek; try { dek = await unwrap(u.pwd, await kekFrom(pwd, unb64(u.kdf.salt), u.kdf.iter), true); } catch (e) { throw new Error('Hasło jest nieprawidłowe.'); }
    const code = newCode(), rsalt = rnd(16), rc = await wrap(dek, await kekFrom(normCode(code), rsalt, G.ITER));
    u.rec = { salt: b64(rsalt), iter: G.ITER, iv: rc.iv, ct: rc.ct }; saveUsers(us); return code;
  };
  G.deleteUser = async function (pwd) {
    const us = G.users(), u = us.find(x => x.id === G.user.id);
    try { await unwrap(u.pwd, await kekFrom(pwd, unb64(u.kdf.salt), u.kdf.iter), false); } catch (e) { throw new Error('Hasło jest nieprawidłowe.'); }
    const id = u.id;
    for (const n of ['opisyNFZ@' + id, 'gabinet@' + id]) { try { await idbReq(indexedDB.deleteDatabase(n)); } catch (e) { } }
    try { const ks = []; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); if (k && (k.includes('@' + id + '.') || k === K_PREFS + id)) ks.push(k); } ks.forEach(lsDel); } catch (e) { }
    saveUsers(us.filter(x => x.id !== id)); await sessDel(); lsDel(K_CUR); return true;
  };

  /* ---------- sesja ---------- */
  let sdb = null;
  async function sessDb() { if (!sdb) sdb = await idbOpen(SESS_DB, ['s']); return sdb; }
  async function sessStart(uid, key) { const db = await sessDb(); const now = Date.now(); await run(db, ['s'], 'readwrite', t => { t.objectStore('s').put({ uid, key, last: now, start: now }, 'cur'); }); setHint(uid); }
  async function sessGet() { const db = await sessDb(); return run(db, ['s'], 'readonly', t => t.objectStore('s').get('cur')); }
  async function sessDel() { try { const db = await sessDb(); await run(db, ['s'], 'readwrite', t => { t.objectStore('s').delete('cur'); }); } catch (e) { } }
  async function sessTouch(at) { try { const db = await sessDb(); await run(db, ['s'], 'readwrite', t => { const o = t.objectStore('s'), r = o.get('cur'); r.onsuccess = () => { const s = r.result; if (s) { s.last = Math.max(s.last || 0, at || Date.now()); o.put(s, 'cur'); } }; }); } catch (e) { } }
  G._sessGet = () => sessGet();
  const expired = s => !s || (Date.now() - (s.last || 0)) > G.prefs(s.uid).lockMin * 60000;
  G.session = async () => { const s = await sessGet().catch(() => null); return s && !expired(s) && G.users().some(u => u.id === s.uid) ? s : null; };
  G.logout = async () => { await sessDel(); G.user = null; G.key = null; };

  function goLogin(mod, why) { location.replace('index.html?' + (mod && mod !== 'start' ? 'wroc=' + encodeURIComponent(mod) + '&' : '') + (why ? 'p=' + why : '')); }
  G.goLogin = goLogin;

  /* gotowość modułu: ważna sesja albo przejście do logowania (obietnica wtedy nigdy się nie spełnia) */
  G.ready = function (mod) {
    if (G._ready) return G._ready;
    G.mod = mod;
    G._ready = (async () => {
      const s = await G.session();
      const hint = G.hint();
      if (!s || (hint && s.uid !== hint)) { await sessDel(); goLogin(mod, s ? '' : 'blokada'); return new Promise(() => { }); }
      const u = G.users().find(x => x.id === s.uid);
      G.user = { id: u.id, name: u.name }; G.key = s.key; setHint(u.id);
      await sessTouch(Date.now());
      try { if (navigator.storage && navigator.storage.persist) navigator.storage.persist().catch(() => { }); } catch (e) { }
      watch(mod);
      G.bar(mod);
      return G.user;
    })();
    return G._ready;
  };

  /* ---------- aktywność i blokada ---------- */
  const lockHooks = [];
  G.onLock = fn => lockHooks.push(fn);
  let act = Date.now(), sentAct = 0, sentAt = 0, watching = false, locking = false;
  function watch(mod) {
    if (watching) return; watching = true;
    const mark = () => { act = Date.now(); };
    ['pointerdown', 'keydown', 'touchstart', 'wheel', 'input'].forEach(e => document.addEventListener(e, mark, { capture: true, passive: true }));
    const tick = async () => {
      if (locking) return;
      if (act > sentAct && Date.now() - sentAt >= 15000) { sentAct = act; sentAt = Date.now(); await sessTouch(act); }
      const s = await sessGet().catch(() => null);
      if (!s || s.uid !== (G.user && G.user.id)) { G.lock('inna-karta'); return; }
      if (expired(s)) G.lock('bezczynnosc');
    };
    setInterval(tick, 10000);
    document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') tick(); });
  }
  G.lock = async function (why) {
    if (locking) return; locking = true;
    await Promise.race([Promise.all(lockHooks.map(f => Promise.resolve().then(f).catch(() => { }))), new Promise(r => setTimeout(r, 1500))]);
    if (why !== 'inna-karta') await sessDel();
    goLogin(G.mod, 'blokada');
  };
  G.leave = async function (href) { await Promise.race([Promise.all(lockHooks.map(f => Promise.resolve().then(f).catch(() => { }))), new Promise(r => setTimeout(r, 1200))]); location.href = href; };
  G.switchUser = async function () { await Promise.race([Promise.all(lockHooks.map(f => Promise.resolve().then(f).catch(() => { }))), new Promise(r => setTimeout(r, 1500))]); await sessDel(); lsDel(K_CUR); location.replace('index.html'); };

  /* ---------- pasek modułów ---------- */
  const LOGO = '<svg viewBox="0 0 32 32" width="22" height="22" aria-hidden="true"><path d="M16 4c-3 0-4.4 1.6-7 1.6C5.8 5.6 4 8 4 11.6c0 5.6 2.3 15.4 5.6 15.4 2.3 0 2.2-6.6 6.4-6.6s4.1 6.6 6.4 6.6c3.3 0 5.6-9.8 5.6-15.4C28 8 26.2 5.6 23 5.6 20.4 5.6 19 4 16 4z" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/></svg>';
  G.bar = function (mod) {
    let el = document.getElementById('gbar');
    if (!el) { el = document.createElement('header'); el.id = 'gbar'; document.body.insertBefore(el, document.body.firstChild); }
    el.className = 'gbar'; el.setAttribute('role', 'banner');
    const name = (G.user && G.user.name) || ((G.users().find(u => u.id === G.hint()) || {}).name) || '';
    el.innerHTML = '<div class="gbar-in"><a class="gbar-home' + (mod === 'start' ? ' on' : '') + '" href="index.html" aria-label="Strona główna">' + LOGO + '<span>Gabinet</span></a>' +
      '<nav class="gbar-nav" aria-label="Moduły">' + MODS.map(m => '<a href="' + m.href + '" data-gmod="' + m.id + '"' + (m.id === mod ? ' class="on" aria-current="page"' : '') + '>' + m.name + '</a>').join('') + '</nav>' +
      (name ? '<div class="gbar-user"><button type="button" class="gbar-ubtn" aria-haspopup="true" aria-expanded="false"><span class="gbar-av">' + esc(name.charAt(0).toUpperCase()) + '</span><span class="gbar-un">' + esc(name) + '</span></button>' +
        '<div class="gbar-menu" hidden><a href="index.html#konto">Konto i bezpieczeństwo</a><button type="button" data-g="lock">Zablokuj</button><button type="button" data-g="switch">Zmień użytkownika</button></div></div>' : '') + '</div>';
    el.querySelectorAll('a[href]').forEach(a => a.addEventListener('click', e => {   // przed przejściem: moduł zapisuje szkic
      if (e.defaultPrevented || e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
      e.preventDefault(); G.leave(a.getAttribute('href'));
    }));
    const b = el.querySelector('.gbar-ubtn'), m = el.querySelector('.gbar-menu');
    if (b) {
      b.onclick = e => { e.stopPropagation(); const o = m.hidden; m.hidden = !o; b.setAttribute('aria-expanded', String(o)); };
      document.addEventListener('click', e => { if (!m.hidden && !el.contains(e.target)) { m.hidden = true; b.setAttribute('aria-expanded', 'false'); } });
      el.querySelector('[data-g="lock"]').onclick = () => G.lock('reczna');
      el.querySelector('[data-g="switch"]').onclick = () => G.switchUser();
    }
  };

  /* ---------- magazyn użytkownika: IndexedDB „gabinet@<id>” ---------- */
  const STORES = ['kv', 'wizyty', 'opisy', 'szkice'];
  let udb = null;
  async function userDb() { if (!udb) udb = await idbOpen('gabinet@' + G.user.id, STORES); return udb; }
  G.store = function (name) {
    const aad = k => 'g:' + name + ':' + k;
    return {
      async get(k) { const db = await userDb(); const v = await run(db, [name], 'readonly', t => t.objectStore(name).get(k)); return v === undefined ? undefined : dec(v, aad(k)); },
      async put(k, v) { const s = await enc(v, aad(k)); const db = await userDb(); await run(db, [name], 'readwrite', t => { t.objectStore(name).put(s, k); }); },
      async putMany(rows) { const e2 = await Promise.all(rows.map(([k, v]) => enc(v, aad(k)).then(s => [k, s]))); const db = await userDb(); await run(db, [name], 'readwrite', t => { const o = t.objectStore(name); e2.forEach(([k, s]) => o.put(s, k)); }); },
      async del(k) { const db = await userDb(); await run(db, [name], 'readwrite', t => { t.objectStore(name).delete(k); }); },
      async all() {
        const rows = await readAll(await userDb(), name);
        const out = await Promise.all(rows.map(([k, v]) => dec(v, aad(k)).then(x => [k, x], () => null)));
        return out.filter(Boolean);
      },
      async raw(k) { const db = await userDb(); return run(db, [name], 'readonly', t => t.objectStore(name).get(k)); }
    };
  };

  /* warstwa szyfrująca dla magazynu Opisów NFZ (interfejs DB.be: all / get / write / clear) */
  G.wrapBE = function (be, ns) {
    const aad = (s, k) => ns + ':' + s + ':' + k;
    return { kind: be.kind, enc: true,
      async all(store) { const rows = await be.all(store); const out = await Promise.all(rows.map(([k, v]) => dec(v, aad(store, k)).then(x => [k, x], () => null))); G.undecrypted = (G.undecrypted || 0) + out.filter(x => !x).length; return out.filter(Boolean); },
      async get(store, key) { const v = await be.get(store, key); if (v === undefined || v === null) return undefined; try { return await dec(v, aad(store, key)); } catch (e) { return undefined; } },
      async write(ops) { const o2 = await Promise.all(ops.map(o => o.del ? o : enc(o.val, aad(o.s, o.key)).then(s => ({ s: o.s, key: o.key, val: s })))); return be.write(o2); },
      clear(stores) { return be.clear(stores); } };
  };

  /* ---------- szkice, sumy dzienne, gabinety ---------- */
  G.draft = {
    save: (mod, v) => G.store('szkice').put(mod, Object.assign({ at: new Date().toISOString() }, v)).catch(() => { }),
    load: mod => G.store('szkice').get(mod).catch(() => undefined),
    clear: mod => G.store('szkice').del(mod).catch(() => { })
  };
  G.sums = { put: (kind, map) => G.store('kv').put('suma:' + kind, map), get: kind => G.store('kv').get('suma:' + kind).catch(() => undefined) };
  let grafikCache = null;
  G.grafik = async (fresh) => { if (fresh || !grafikCache) grafikCache = (await G.store('kv').get('grafik').catch(() => null)) || null; return grafikCache; };
  G.clinics = async (all) => { const d = await G.grafik(); const cs = d && d.settings && Array.isArray(d.settings.clinics) ? d.settings.clinics : []; return cs.filter(c => all || c.active !== false).map(c => ({ id: c.id, name: c.name, short: c.short, color: c.color, active: c.active !== false })); };
  G.dayClinic = async (date, hhmm) => {
    const d = await G.grafik(); if (!d) return '';
    const m = d['m' + String(date).slice(0, 7)]; const sh = m && Array.isArray(m.shifts) ? m.shifts.filter(s => s.date === date && s.status !== 'cancelled') : [];
    if (!sh.length) return '';
    if (hhmm) { const hit = sh.find(s => s.start <= hhmm && hhmm < s.end); if (hit) return hit.clinicId; }
    return sh.slice().sort((a, b) => String(a.start).localeCompare(String(b.start)))[0].clinicId;
  };

  /* ---------- dane z poprzednich wersji (jawne) → przestrzeń pierwszego użytkownika ---------- */
  function idbExisting(name) {
    return new Promise(res => {
      let rq, created = false; try { rq = indexedDB.open(name); } catch (e) { res(null); return; }
      rq.onupgradeneeded = e => { if (e.oldVersion === 0) { created = true; try { rq.transaction.abort(); } catch (_) { } } };
      rq.onsuccess = () => { const db = rq.result; if (created || !db.objectStoreNames.length) { try { db.close(); } catch (e) { } if (created) indexedDB.deleteDatabase(name); res(null); } else res(db); };
      rq.onerror = () => res(null);
    });
  }
  async function readAll(db, store) {
    if (!db.objectStoreNames.contains(store)) return [];
    let ks = [], vs = [];
    await run(db, [store], 'readonly', t => { const o = t.objectStore(store), a = o.getAllKeys(), b = o.getAll(); a.onsuccess = () => { ks = a.result; }; b.onsuccess = () => { vs = b.result; }; });
    return ks.map((k, i) => [k, vs[i]]);
  }
  function lsKeys(pre) { const o = []; try { for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); if (k && k.startsWith(pre)) o.push(k); } } catch (e) { } return o; }
  G.legacy = {
    async detect() {
      const r = { nfz: 0, nfzLS: 0, nfzV9: 0, grafik: null };
      const db = await idbExisting('opisyNFZ');
      if (db) { r.nfz = (await readAll(db, 'visits')).length; try { db.close(); } catch (e) { } }
      r.nfzLS = lsKeys('opisyNFZ2.visits.').length;
      const h = lsGet('opisyNFZ.hidx', null); r.nfzV9 = Array.isArray(h) ? h.length : 0;
      r.nfzCfg = localStorage.getItem('opisyNFZ.cfg') !== null;
      const g = lsGet('grafik-gabinetow-v1', null);
      if (g && typeof g === 'object') { let n = 0; Object.keys(g).forEach(k => { if (/^m\d{4}-\d{2}$/.test(k) && g[k] && Array.isArray(g[k].shifts)) n += g[k].shifts.length; }); r.grafik = { shifts: n, clinics: g.settings && Array.isArray(g.settings.clinics) ? g.settings.clinics.length : 0 }; }
      r.any = !!(r.nfz || r.nfzLS || r.nfzV9 || r.nfzCfg || r.grafik);
      return r;
    },
    /* szyfruje, sprawdza i dopiero potem kasuje wersje jawne; zwraca podsumowanie */
    async migrate() {
      const uid = G.user.id, out = { nfz: 0, nfzLS: 0, nfzV9: 0, grafik: false, errors: [] };
      // 1. Opisy NFZ – IndexedDB „opisyNFZ”
      const old = await idbExisting('opisyNFZ');
      if (old) {
        try {
          const nu = await idbOpen('opisyNFZ@' + uid, ['visits', 'bodies', 'segs']);
          let total = 0;
          for (const s of ['visits', 'bodies', 'segs']) {
            const rows = await readAll(old, s); total += rows.length;
            const encd = await Promise.all(rows.map(([k, v]) => enc(v, 'nfz:' + s + ':' + k).then(x => [k, x])));
            await run(nu, [s], 'readwrite', t => { const o = t.objectStore(s); encd.forEach(([k, x]) => o.put(x, k)); });
            if (s === 'visits') out.nfz = rows.length;
          }
          let n2 = 0; for (const s of ['visits', 'bodies', 'segs']) n2 += (await readAll(nu, s)).length;
          const sample = (await readAll(nu, 'visits'))[0];
          if (n2 < total || (sample && !(await dec(sample[1], 'nfz:visits:' + sample[0]).then(() => true, () => false)))) throw new Error('kontrola przeniesienia nie przeszła');
          try { nu.close(); } catch (e) { } try { old.close(); } catch (e) { }
          await idbReq(indexedDB.deleteDatabase('opisyNFZ')).catch(() => { });
        } catch (e) { out.errors.push('Opisy NFZ: ' + (e && e.message || e)); try { old.close(); } catch (_) { } }
      }
      // 2. Opisy NFZ – zapis awaryjny w localStorage (opisyNFZ2.*) – szyfrowany pod kluczami użytkownika
      for (const k of lsKeys('opisyNFZ2.')) {
        try { const rest = k.slice('opisyNFZ2.'.length), i = rest.indexOf('.'), s = rest.slice(0, i), key = rest.slice(i + 1);
          const v = JSON.parse(localStorage.getItem(k)); const x = await enc(v, 'nfz:' + s + ':' + key);
          localStorage.setItem('opisyNFZ2@' + uid + '.' + rest, JSON.stringify(x)); localStorage.removeItem(k); if (s === 'visits') out.nfzLS++;
        } catch (e) { out.errors.push('zapis awaryjny: ' + (e && e.message || e)); }
      }
      // 3. Opisy NFZ – ustawienia i historia z wersji sprzed bazy (przeniesie ją sam moduł przy pierwszym otwarciu)
      for (const k of lsKeys('opisyNFZ.')) {
        if (k === 'opisyNFZ.probe') { lsDel(k); continue; }
        try { const nk = 'opisyNFZ@' + uid + '.' + k.slice('opisyNFZ.'.length); if (localStorage.getItem(nk) === null) localStorage.setItem(nk, localStorage.getItem(k)); localStorage.removeItem(k); if (k === 'opisyNFZ.hidx') { const h = lsGet(nk, []); out.nfzV9 = Array.isArray(h) ? h.length : 0; } } catch (e) { out.errors.push(k + ': ' + (e && e.message || e)); }
      }
      // 4. Kalendarz (Grafik Gabinetów)
      const g = lsGet('grafik-gabinetow-v1', null);
      if (g && typeof g === 'object') {
        try { await G.store('kv').put('grafik', g); const back = await G.store('kv').get('grafik');
          if (JSON.stringify(back) !== JSON.stringify(g)) throw new Error('kontrola przeniesienia nie przeszła');
          lsDel('grafik-gabinetow-v1'); out.grafik = true; grafikCache = null;
        } catch (e) { out.errors.push('Kalendarz: ' + (e && e.message || e)); }
      }
      const ui = localStorage.getItem('grafik-ui'); if (ui !== null) { try { localStorage.setItem('grafik@' + uid + '.ui', ui); lsDel('grafik-ui'); } catch (e) { } }
      return out;
    }
  };

  /* ---------- liczby: grosze ---------- */
  G.zl = c => (Math.round(c) / 100).toLocaleString('pl-PL', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' zł';
  G.today = () => { const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); };
})();
