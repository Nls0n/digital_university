var g = Object.defineProperty;
var m = (n, e, t) => e in n ? g(n, e, { enumerable: !0, configurable: !0, writable: !0, value: t }) : n[e] = t;
var s = (n, e, t) => m(n, typeof e != "symbol" ? e + "" : e, t);
class b {
  constructor({
    saveKey: e,
    getKey: t,
    clearKeys: r
  }) {
    s(this, "saveKey");
    s(this, "getKey");
    s(this, "clearKeys");
    this.saveKey = e, this.getKey = t, this.clearKeys = r;
  }
  /**
   * Метод, который сохраняет переданную пару "ключ-значение" в локальном хранилище устройства
   */
  setItem(e, t) {
    return this.saveKey({ key: e, value: t });
  }
  /**
   * Метод, который получает значение из локального хранилища устройства по указанному ключу
   */
  getItem(e) {
    return this.getKey({ key: e });
  }
  /**
   * Метод, который удаляет значение из локального хранилища устройства по указанному ключу
   */
  removeItem(e) {
    return this.saveKey({ key: e, value: null });
  }
  /**
   * Метод, который очищает все ключи, ранее сохраненные ботом в локальном хранилище устройства
   */
  clear() {
    return this.clearKeys();
  }
}
class f {
  constructor({
    saveKey: e,
    getKey: t,
    clearKeys: r
  }) {
    s(this, "saveKey");
    s(this, "getKey");
    s(this, "clearKeys");
    this.saveKey = e, this.getKey = t, this.clearKeys = r;
  }
  /**
   * Метод, который сохраняет переданную пару "ключ-значение" в защищенном хранилище устройства
   */
  setItem(e, t) {
    return this.saveKey({ key: e, value: t });
  }
  /**
   * Метод, который получает значение из защищённого хранилища устройства по указанному ключу
   */
  getItem(e) {
    return this.getKey({ key: e });
  }
  /**
   * Метод, который удаляет значение из защищённого хранилища устройства по указанному ключу
   */
  removeItem(e) {
    return this.saveKey({ key: e, value: null });
  }
  /**
   * Метод, который очищает все ключи, ранее сохраненные ботом в защищённом хранилище устройства
   */
  clear() {
    return this.clearKeys();
  }
}
class w {
  constructor({
    postBackButtonEvent: e,
    onClick: t,
    offClick: r
  }) {
    s(this, "visible", !1);
    s(this, "postBackButtonEvent");
    s(this, "onClick");
    s(this, "offClick");
    this.postBackButtonEvent = e, this.onClick = t, this.offClick = r;
  }
  get isVisible() {
    return this.visible;
  }
  show() {
    this.visible = !0, this.postBackButtonEvent(!0);
  }
  hide() {
    this.visible = !1, this.postBackButtonEvent(!1);
  }
}
const o = class o {
  constructor() {
    s(this, "rawInitData");
    s(this, "rawPlatformData");
    s(this, "rawVersionData");
    this.rawInitData = this.getParamFromHashOrStorage(o.WEB_APP_DATA_KEY), this.rawPlatformData = this.getParamFromHashOrStorage(o.WEB_APP_PLATFORM_KEY), this.rawVersionData = this.getParamFromHashOrStorage(o.WEB_APP_VERSION_KEY);
  }
  /**
   * Получает параметр из URL хэша, а если не найден - из sessionStorage.
   * При нахождении в хэше сохраняет значение в sessionStorage.
   * @param paramName - название параметра для поиска
   * @returns значение параметра или null
   */
  getParamFromHashOrStorage(e) {
    const t = this.extractParamFromHashes(e);
    return t ? (sessionStorage.setItem(e, t), t) : sessionStorage.getItem(e);
  }
  /**
   * Извлекает параметр из всех доступных URL хэшей.
   * Проверяет текущий location.hash и navigation entry hash.
   * @param paramName - название параметра для извлечения
   * @returns значение параметра или null
   */
  extractParamFromHashes(e) {
    try {
      const t = this.getHashParam(location.hash, e);
      if (t) return t;
      const r = performance.getEntriesByType("navigation")[0], i = r && new URL(r.name).hash, a = i && this.getHashParam(i, e);
      return a || null;
    } catch (t) {
      return console.warn(`Ошибка при извлечении параметра ${e}:`, t), null;
    }
  }
  /**
   * Универсальный метод для получения параметра из хэша.
   * @param hash - хэш для парсинга
   * @param paramName - название параметра для извлечения
   * @returns значение параметра или null
   */
  getHashParam(e, t) {
    try {
      const r = e.replace(/^#/, "");
      return new URLSearchParams(r).get(t);
    } catch (r) {
      return console.warn(`Ошибка при извлечении параметра ${t}:`, r), null;
    }
  }
  /**
   * Геттер для получения сырых данных инициализации.
   * @returns строка с закодированными данными инициализации или null
   */
  get initData() {
    return this.rawInitData;
  }
  /**
   * Геттер для получения платформы.
   * @returns платформа или null
   */
  get platform() {
    return this.isValidPlatform(this.rawPlatformData) ? this.rawPlatformData : null;
  }
  get version() {
    return this.rawVersionData;
  }
  /**
   * Проверяет является ли строка валидной платформой.
   */
  isValidPlatform(e) {
    return e !== null && o.VALID_PLATFORMS.includes(e);
  }
  /**
   * Геттер для получения распарсенных данных инициализации.
   * @returns объект с распарсенными данными пользователя, чата и другой информации
   */
  get initDataUnsafe() {
    return this.parseInitData(this.rawInitData);
  }
  /**
   * Парсит строку с данными инициализации в объект.
   * @param initData - закодированная строка с данными инициализации
   * @returns объект с распарсенными данными
   */
  parseInitData(e) {
    const t = {};
    if (!e)
      return t;
    try {
      const r = decodeURIComponent(e);
      new URLSearchParams(r).forEach((a, c) => {
        switch (c) {
          case "hash":
          case "ip":
          case "query_id":
          case "start_param": {
            t[c] = a;
            break;
          }
          case "auth_date": {
            t[c] = Number(a);
            break;
          }
          case "user": {
            t[c] = this.getUserInitData(a);
            break;
          }
          case "chat": {
            t[c] = this.getChatInitData(a);
            break;
          }
          default:
            console.warn(`Неизвестный параметр: ${c}`);
        }
      });
    } catch (r) {
      console.warn("Ошибка при парсинге init data:", r);
    }
    return t;
  }
  /**
   * Парсит JSON строку с данными пользователя.
   * @param userString - JSON строка с данными пользователя
   * @returns объект с данными пользователя или undefined при ошибке
   */
  getUserInitData(e) {
    try {
      const t = JSON.parse(e);
      if (t && typeof t == "object")
        return {
          first_name: t.first_name,
          last_name: t.last_name,
          username: t.username,
          language_code: t.language_code,
          photo_url: t.photo_url,
          id: Number(t.id)
        };
    } catch (t) {
      console.warn("Ошибка при парсинге данных пользователя:", t);
    }
  }
  /**
   * Парсит JSON строку с данными чата.
   * @param chatString - JSON строка с данными чата
   * @returns объект с данными чата или undefined при ошибке
   */
  getChatInitData(e) {
    try {
      const t = JSON.parse(e);
      if (t && typeof t == "object")
        return {
          id: t.id,
          type: t.type
        };
    } catch (t) {
      console.warn("Ошибка при парсинге данных чата:", t);
    }
  }
};
s(o, "WEB_APP_DATA_KEY", "WebAppData"), s(o, "WEB_APP_PLATFORM_KEY", "WebAppPlatform"), s(o, "WEB_APP_VERSION_KEY", "WebAppVersion"), s(o, "VALID_PLATFORMS", [
  "ios",
  "android",
  "desktop",
  "web"
]);
let p = o;
const y = (n) => typeof n.requestId == "string" && n.requestId.length > 0, h = (n, e) => {
  throw console.error(`[WebApp] ${e}`), {
    error: {
      code: n
    }
  };
}, v = (n) => {
  var t;
  const e = n.split("WebApp")[1];
  return e ? (t = e.match(/([A-Z][a-z]*)/g)) == null ? void 0 : t.map((r) => r.toLowerCase()).join("_") : "unknown_method";
}, S = 1e4, u = 6e4, q = 6e5;
function A() {
  if (crypto && (crypto != null && crypto.randomUUID))
    return crypto.randomUUID();
  if (crypto && (crypto != null && crypto.getRandomValues)) {
    const e = new Uint8Array(16);
    crypto.getRandomValues(e);
    let t = "";
    for (let r = 0; r < e.length; r++)
      t += e[r].toString(16).padStart(2, "0");
    return t;
  }
  let n = Date.now().toString(36);
  for (; n.length < 32; )
    n += Math.random().toString(36).slice(2);
  return n.slice(0, 32);
}
class I {
  constructor({
    getInfo: e,
    requestBiometryAccess: t,
    updateToken: r,
    requestAuth: i,
    openSettings: a
  }) {
    s(this, "getInfo");
    s(this, "requestBiometryAccess");
    s(this, "updateToken");
    s(this, "requestAuth");
    s(this, "_openSettings");
    s(this, "inited", !1);
    s(this, "biometryInfo", {
      available: !1,
      accessRequested: !1,
      accessGranted: !1,
      type: ["unknown"],
      tokenSaved: !1,
      deviceId: null
    });
    this.getInfo = e, this.requestBiometryAccess = t, this.updateToken = r, this.requestAuth = i, this._openSettings = a;
  }
  getBiometryInfo() {
    return { ...this.biometryInfo };
  }
  setBiometryInfo(e) {
    this.biometryInfo = { ...this.biometryInfo, ...e };
  }
  checkInit(e, t = "BiometricManager должен быть инициализирован перед использованием.") {
    return this.inited || h(e, t), !0;
  }
  checkAccessGranted(e, t = "Биометрический доступ не предоставлен пользователем.") {
    return this.biometryInfo.accessGranted || h(e, t), !0;
  }
  checkAvailable(e, t = "Биометрические данные недоступны на этом устройстве.") {
    return this.biometryInfo.available || h(e, t), !0;
  }
  get isInited() {
    return this.inited;
  }
  get isBiometricAvailable() {
    return this.biometryInfo.available;
  }
  get isAccessRequested() {
    return this.biometryInfo.accessRequested;
  }
  get isAccessGranted() {
    return this.biometryInfo.accessGranted;
  }
  get isBiometricTokenSaved() {
    return this.biometryInfo.tokenSaved;
  }
  get biometricType() {
    return this.biometryInfo.type;
  }
  get deviceId() {
    return this.biometryInfo.deviceId;
  }
  // Инициализация
  async init() {
    if (this.inited)
      return this.getBiometryInfo();
    const e = await this.getInfo();
    return this.setBiometryInfo(e), this.inited = !0, this.getBiometryInfo();
  }
  // Запрос доступа
  async requestAccess(e) {
    if (this.biometryInfo.accessRequested)
      return this.getBiometryInfo();
    this.checkInit("client.biometry_request_access.not_inited"), this.checkAvailable("client.biometry_request_access.not_supported");
    const t = await this.requestBiometryAccess({ reason: e });
    return this.setBiometryInfo(t), this.getBiometryInfo();
  }
  // Аутентификация
  async authenticate(e) {
    return this.checkInit("client.biometry_request_auth.not_inited"), this.checkAvailable("client.biometry_request_auth.not_supported"), this.checkAccessGranted("client.biometry_request_auth.permission_denied"), this.biometryInfo.tokenSaved || h("client.biometry_request_auth.not_found", "Биометрический токен не найден."), this.requestAuth({ reason: e });
  }
  // Обновление биометрического токена
  async updateBiometricToken(e, t) {
    this.checkInit("client.biometry_update_token.not_inited"), this.checkAvailable("client.biometry_update_token.not_supported"), this.checkAccessGranted("client.biometry_update_token.permission_denied");
    const r = await this.updateToken({ token: e, reason: t });
    return this.biometryInfo.tokenSaved = r.status === "updated", r;
  }
  // Открытие настроек биометрии бота
  async openSettings() {
    return this.checkInit("client.biometry_open_settings.not_inited"), this.checkAvailable("client.biometry_open_settings.not_supported"), this.biometryInfo.accessGranted && h(
      "client.biometry_open_settings.permission_denied",
      "Биометрический доступ уже предоставлен пользователем. Нет необходимости открывать настройки."
    ), this._openSettings();
  }
}
class E {
  constructor({ impactOccurred: e, notificationOccurred: t, selectionChanged: r }) {
    s(this, "_impactOccurred");
    s(this, "_notificationOccurred");
    s(this, "_selectionChanged");
    this._impactOccurred = e, this._notificationOccurred = t, this._selectionChanged = r;
  }
  impactOccurred(e, t = !1) {
    return this._impactOccurred({
      impactStyle: e,
      disableVibrationFallback: t
    });
  }
  notificationOccurred(e, t = !1) {
    return this._notificationOccurred({
      notificationType: e,
      disableVibrationFallback: t
    });
  }
  selectionChanged(e = !1) {
    return this._selectionChanged({
      disableVibrationFallback: e
    });
  }
}
class C {
  constructor({ postSwipesBehaviorEvent: e }) {
    s(this, "enabled", !0);
    s(this, "postSwipesBehaviorEvent");
    this.postSwipesBehaviorEvent = e;
  }
  get isEnabled() {
    return this.enabled;
  }
  async enable() {
    const e = await this.postSwipesBehaviorEvent({ allowVerticalSwipes: !0 });
    return this.enabled = e.allowVerticalSwipes, e;
  }
  async disable() {
    const e = await this.postSwipesBehaviorEvent({ allowVerticalSwipes: !1 });
    return this.enabled = e.allowVerticalSwipes, e;
  }
}
class _ {
  constructor({ postScreenCaptureEvent: e }) {
    s(this, "enabled", !1);
    s(this, "postScreenCaptureEvent");
    this.postScreenCaptureEvent = e;
  }
  get isScreenCaptureEnabled() {
    return this.enabled;
  }
  async enableScreenCapture() {
    const e = await this.postScreenCaptureEvent({ isScreenCaptureEnabled: !0 });
    return this.enabled = e.isScreenCaptureEnabled, e;
  }
  async disableScreenCapture() {
    const e = await this.postScreenCaptureEvent({ isScreenCaptureEnabled: !1 });
    return this.enabled = e.isScreenCaptureEnabled, e;
  }
}
const B = /^https:\/\/.*\.(?:max|oneme)\.ru$/;
class R {
  constructor(e) {
    s(this, "webviewBridge");
    s(this, "messageCallback");
    s(this, "sendEvent");
    this.messageCallback = e, this.isIframe() ? (this.sendEvent = this.sendOverIframe, this.initializeIframeTransport()) : typeof window < "u" && window.WebViewHandler ? (this.webviewBridge = window.WebViewHandler, this.sendEvent = this.sendOverWebView) : this.sendEvent = this.sendFallback;
  }
  isIframe() {
    return typeof window < "u" && window.self !== window.top;
  }
  initializeIframeTransport() {
    window.addEventListener("message", async (e) => {
      if (!(!B.test(e.origin) || typeof e.data != "string"))
        try {
          const { type: t, ...r } = JSON.parse(e.data);
          t != null && t.startsWith("WebApp") && this.messageCallback && this.messageCallback(t, r);
        } catch (t) {
          console.error("[WebApp] Ошибка при обработке сообщения: ", t);
        }
    });
  }
  sendOverIframe(e, t) {
    window.parent.postMessage(JSON.stringify({ type: e, ...t }), "*");
  }
  sendOverWebView(e, t) {
    var r;
    (r = this.webviewBridge) == null || r.postEvent(e, JSON.stringify(t));
  }
  sendFallback(e) {
    console.warn("[WebApp] Событие не отправлено - транспорт недоступен:", e);
  }
}
class k {
  constructor(e) {
    s(this, "pendingRequests", /* @__PURE__ */ new Map());
    s(this, "sendEvent");
    this.sendEvent = e;
  }
  /**
   * Отправка события с ожиданием ответа
   */
  createRequest(e, t = {}, r = {}) {
    const { timeout: i = S } = r;
    return new Promise((a, c) => {
      const l = A(), d = setTimeout(() => {
        this.deletePendingRequest(l), c({
          error: {
            code: `client.${v(e)}.request_timeout`
          }
        });
      }, i);
      this.pendingRequests.set(l, { resolve: a, reject: c, timeoutId: d }), this.sendEvent(e, { ...t, requestId: l });
    });
  }
  /**
   * Обработка ответа на запрос
   * Вызывается только когда eventData.requestId существует
   */
  handleResponse(e, t) {
    const { requestId: r, ...i } = t, a = this.pendingRequests.get(r);
    if (!a) {
      console.warn(`[WebApp] Получен ответ на неизвестный запрос: ${e}`);
      return;
    }
    "error" in i ? (console.error(`[WebApp] Получена ошибка: ${e}`, i), a.reject(i)) : (console.log(`[WebApp] Получено событие: ${e}`, i), a.resolve(i)), this.clearTimeout(r), this.deletePendingRequest(r);
  }
  clearTimeout(e) {
    const t = this.pendingRequests.get(e);
    t && clearTimeout(t.timeoutId);
  }
  deletePendingRequest(e) {
    this.pendingRequests.get(e) && this.pendingRequests.delete(e);
  }
}
class W {
  constructor() {
    s(this, "eventHandlers", /* @__PURE__ */ new Map());
    s(this, "transport");
    s(this, "requestController");
    s(this, "initDataManager");
    s(this, "swipesBehaviorManager");
    s(this, "SecureStorage");
    s(this, "DeviceStorage");
    s(this, "BackButton");
    s(this, "BiometricManager");
    s(this, "HapticFeedback");
    s(this, "ScreenCapture");
    /**
     * Обёртка для автоматического добавления query_id к параметрам
     */
    s(this, "withQueryId", (e) => (t = {}) => {
      var i;
      const r = (i = this.initDataUnsafe) == null ? void 0 : i.query_id;
      return e({ ...t || {}, queryId: r });
    });
    this.transport = new R(async (e, t) => {
      await this.receiveEvent(e, t);
    }), this.requestController = new k((e, t) => {
      this.transport.sendEvent(e, t);
    }), this.BackButton = new w({
      postBackButtonEvent: (e) => this.postEvent("WebAppSetupBackButton", { isVisible: e }),
      onClick: (e) => this.onEvent("WebAppBackButtonPressed", e),
      offClick: (e) => this.offEvent("WebAppBackButtonPressed", e)
    }), this.initDataManager = new p(), this.SecureStorage = new f({
      saveKey: this.withQueryId(
        (e) => this.requestController.createRequest("WebAppSecureStorageSaveKey", e)
      ),
      getKey: this.withQueryId(
        (e) => this.requestController.createRequest("WebAppSecureStorageGetKey", e)
      ),
      clearKeys: this.withQueryId(
        (e) => this.requestController.createRequest("WebAppSecureStorageClear", e)
      )
    }), this.DeviceStorage = new b({
      saveKey: this.withQueryId(
        (e) => this.requestController.createRequest("WebAppDeviceStorageSaveKey", e)
      ),
      getKey: this.withQueryId(
        (e) => this.requestController.createRequest("WebAppDeviceStorageGetKey", e)
      ),
      clearKeys: this.withQueryId(
        (e) => this.requestController.createRequest("WebAppDeviceStorageClear", e)
      )
    }), this.BiometricManager = new I({
      getInfo: this.withQueryId(
        (e) => this.requestController.createRequest("WebAppBiometryGetInfo", e)
      ),
      requestBiometryAccess: this.withQueryId(
        (e) => this.requestController.createRequest("WebAppBiometryRequestAccess", e, {
          timeout: u
        })
      ),
      updateToken: this.withQueryId(
        (e) => this.requestController.createRequest("WebAppBiometryUpdateToken", e, {
          timeout: u
        })
      ),
      requestAuth: this.withQueryId(
        (e) => this.requestController.createRequest("WebAppBiometryRequestAuth", e, {
          timeout: u
        })
      ),
      openSettings: this.withQueryId(
        (e) => this.requestController.createRequest("WebAppBiometryOpenSettings", e, {
          timeout: u
        })
      )
    }), this.HapticFeedback = new E({
      impactOccurred: (e) => this.requestController.createRequest("WebAppHapticFeedbackImpact", e),
      notificationOccurred: (e) => this.requestController.createRequest("WebAppHapticFeedbackNotification", e),
      selectionChanged: (e) => this.requestController.createRequest("WebAppHapticFeedbackSelectionChange", e)
    }), this.swipesBehaviorManager = new C({
      postSwipesBehaviorEvent: (e) => this.requestController.createRequest("WebAppSetupSwipesBehavior", e)
    }), this.ScreenCapture = new _({
      postScreenCaptureEvent: (e) => this.requestController.createRequest("WebAppSetupScreenCaptureBehavior", e)
    });
  }
  /**
   * Сырые данные инициализации
   */
  get initData() {
    return this.initDataManager.initData;
  }
  /**
   * Распарсенные данные инициализации
   */
  get initDataUnsafe() {
    return this.initDataManager.initDataUnsafe;
  }
  get platform() {
    return this.initDataManager.platform;
  }
  get version() {
    return this.initDataManager.version;
  }
  /**
   * Состояние вертикальных свайпов
   */
  get isVerticalSwipesEnabled() {
    return this.swipesBehaviorManager.isEnabled;
  }
  /**
   * Стандартная отправка событий (без ожидания ответа)
   */
  postEvent(e, t = {}, r) {
    this.transport.sendEvent(e, t), r == null || r();
  }
  /**
   * Обработка полученного события
   * Простое разделение: requestId есть -> RequestController, нет -> event handlers
   */
  async receiveEvent(e, t) {
    if (y(t))
      this.requestController.handleResponse(e, t);
    else {
      const r = this.eventHandlers.get(e);
      r == null || r.forEach((i) => {
        try {
          i(t);
        } catch (a) {
          console.error(`Ошибка в обработке события "${e}":`, a);
        }
      });
    }
  }
  /**
   * Функция, которую используют нативные клиенты для отправки ответа
   */
  async sendEvent(e, t = "{}") {
    try {
      this.receiveEvent(e, JSON.parse(t));
    } catch (r) {
      console.warn(r);
    }
  }
  /**
   * Подписка на событие с использованием колбэка
   */
  onEvent(e, t) {
    let r = this.eventHandlers.get(e);
    return r || (r = /* @__PURE__ */ new Set(), this.eventHandlers.set(e, r)), r.add(t), () => {
      this.offEvent(e, t);
    };
  }
  /**
   * Удаление подписки на событие
   */
  offEvent(e, t) {
    const r = this.eventHandlers.get(e);
    r && (r.delete(t), r.size === 0 && this.eventHandlers.delete(e));
  }
  /**
   * Изменить яркость экрана на максимум
   * Клиент держит яркость 30 секунд, затем сбрасывает в первоначальное значение
   */
  requestScreenMaxBrightness() {
    return this.requestController.createRequest("WebAppChangeScreenBrightness", {
      maxBrightness: !0
    });
  }
  /**
   * Восстановить яркость экрана
   */
  restoreScreenBrightness() {
    return this.requestController.createRequest("WebAppChangeScreenBrightness", {
      maxBrightness: !1
    });
  }
  /**
   * Закрытие приложения
   */
  close() {
    this.postEvent("WebAppClose", {}, () => {
      console.log("Приложение закрыто");
    });
  }
  /**
   * Инициализация WebApp API
   */
  ready() {
    this.postEvent("WebAppReady", {}, () => {
      console.log("WebApp готово к работе");
    });
  }
  /**
   * Запрос номера телефона
   */
  requestContact() {
    return this.requestController.createRequest(
      "WebAppRequestPhone",
      {},
      {
        timeout: u
      }
    );
  }
  /**
   * Подтверждать закрытие миниаппа с помощью всплывающего окна
   */
  enableClosingConfirmation() {
    this.postEvent("WebAppSetupClosingBehavior", { needConfirmation: !0 });
  }
  /**
   * Отключение подтверждения закрытия миниаппа
   */
  disableClosingConfirmation() {
    this.postEvent("WebAppSetupClosingBehavior", { needConfirmation: !1 });
  }
  /**
   * Открытие ссылки во внешнем браузере
   */
  openLink(e) {
    this.postEvent("WebAppOpenLink", { url: e });
  }
  /**
   * Открытие диплинка связанного с max.ru
   */
  openMaxLink(e) {
    this.postEvent("WebAppOpenMaxLink", { url: e });
  }
  /**
   * Скачивание файла
   */
  downloadFile(e, t) {
    return this.requestController.createRequest(
      "WebAppDownloadFile",
      { url: e, file_name: t },
      {
        timeout: u
      }
    );
  }
  /**
   * Вызов нативного экрана шаринга
   */
  shareContent(e) {
    return this.requestController.createRequest("WebAppShare", e, {
      timeout: u
    });
  }
  /**
   * Шаринг в диалоги/чаты Max
   */
  shareMaxContent(e) {
    return this.requestController.createRequest("WebAppMaxShare", e, {
      timeout: u
    });
  }
  /**
   * Включение вертикальных свайпов
   */
  enableVerticalSwipes() {
    return this.swipesBehaviorManager.enable();
  }
  /**
   * Отключение вертикальных свайпов
   */
  disableVerticalSwipes() {
    return this.swipesBehaviorManager.disable();
  }
  /**
   * Открывает камеру для считывания QR кода и получает результат сканирования.
   */
  openCodeReader(e = !0) {
    return this.requestController.createRequest(
      "WebAppOpenCodeReader",
      { fileSelect: e },
      {
        timeout: q
      }
    );
  }
}
const D = new W();
window.WebApp = D;
