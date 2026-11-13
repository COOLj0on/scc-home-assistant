class SccThermalCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        ha-card { padding: 18px; }
        .header { display: flex; justify-content: space-between; align-items: start; gap: 12px; margin-bottom: 18px; }
        h2 { margin: 0; font-size: 1.25rem; }
        .eyebrow { color: var(--secondary-text-color); font-size: .72rem; letter-spacing: .08em; text-transform: uppercase; margin-bottom: 4px; }
        .layout { display: grid; grid-template-columns: minmax(0, 1fr) 24px minmax(130px, .9fr) 24px minmax(0, 1fr); align-items: center; gap: 10px; }
        .source { min-width: 0; padding: 12px; border-radius: 12px; background: var(--secondary-background-color); }
        .source h3 { display: flex; align-items: center; gap: 8px; margin: 0 0 12px; font-size: .95rem; }
        .source ha-icon { color: var(--state-icon-color); --mdc-icon-size: 20px; }
        .source.solar ha-icon { color: #e8a52a; }
        .source.boiler ha-icon { color: #e46b42; }
        .reading { display: flex; justify-content: space-between; gap: 8px; padding: 7px 0; border-top: 1px solid var(--divider-color); font-size: .84rem; }
        .reading span { color: var(--secondary-text-color); }
        .reading strong { white-space: nowrap; font-variant-numeric: tabular-nums; }
        .pipe { height: 6px; border-radius: 4px; background: var(--divider-color); position: relative; }
        .pipe::after { content: ""; position: absolute; top: -4px; right: -1px; border: 7px solid transparent; border-left-color: var(--divider-color); }
        .pipe.boiler-pipe::after { right: auto; left: -1px; border-left-color: transparent; border-right-color: var(--divider-color); }
        .tank { min-width: 0; }
        .tank-shell { display: flex; flex-direction: column; justify-content: space-around; min-height: 270px; padding: 14px 10px; border: 3px solid var(--divider-color); border-radius: 42px / 18px; background: linear-gradient(180deg, rgba(235, 113, 63, .22), rgba(235, 183, 63, .18) 48%, rgba(75, 151, 214, .22)); box-shadow: inset 0 0 0 5px var(--card-background-color); }
        .probe { display: flex; align-items: center; justify-content: space-between; gap: 5px; padding: 8px 7px; border-radius: 8px; background: var(--card-background-color); font-size: .78rem; }
        .probe::before { content: ""; width: 7px; height: 7px; flex: 0 0 7px; border-radius: 50%; background: var(--primary-color); }
        .probe span { color: var(--secondary-text-color); }
        .probe strong { font-size: .9rem; white-space: nowrap; font-variant-numeric: tabular-nums; }
        .tank-label { margin-top: 8px; color: var(--secondary-text-color); text-align: center; font-size: .78rem; }
        .pumps { display: flex; flex-wrap: wrap; gap: 6px; padding-top: 10px; }
        .pump { display: inline-flex; align-items: center; gap: 5px; padding: 4px 8px; border-radius: 14px; background: var(--divider-color); font-size: .75rem; }
        .pump::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--secondary-text-color); }
        .pump.active { background: rgba(67, 160, 71, .16); }
        .pump.active::before { background: #43a047; box-shadow: 0 0 5px #43a047; }
        .pump.unknown { color: var(--secondary-text-color); }
        .empty, .warning { color: var(--secondary-text-color); font-size: .76rem; }
        .warning { margin-top: 12px; color: var(--error-color); }
        @media (max-width: 560px) {
          ha-card { padding: 14px; }
          .layout { grid-template-columns: minmax(0, 1fr); gap: 8px; }
          .pipe { width: 6px; height: 18px; justify-self: center; }
          .pipe::after { top: auto; right: -4px; bottom: -5px; border-left-color: transparent; border-top-color: var(--divider-color); }
          .tank { grid-row: 1; }
          .solar { grid-row: 2; }
          .pipe.solar-pipe { grid-row: 3; }
          .boiler { grid-row: 4; }
          .pipe.boiler-pipe { display: none; }
          .tank-shell { min-height: 220px; }
        }
      </style>
      <ha-card>
        <div class="header">
          <div>
            <div class="eyebrow">Chriselec SCC · Thermique</div>
            <h2 data-title>Ballon tampon</h2>
          </div>
        </div>
        <div class="layout">
          <section class="source solar">
            <h3><ha-icon icon="mdi:white-balance-sunny"></ha-icon>Panneaux solaires</h3>
            <div class="reading"><span>Départ</span><strong data-role="solar_flow">--</strong></div>
            <div class="reading"><span>Retour</span><strong data-role="solar_return">--</strong></div>
            <div class="pumps" data-pumps="solar_pump"></div>
          </section>
          <div class="pipe solar-pipe"></div>
          <section class="tank">
            <div class="tank-shell">
              <div class="probe"><span>Haut</span><strong data-role="tank_top">--</strong></div>
              <div class="probe"><span>Milieu</span><strong data-role="tank_middle">--</strong></div>
              <div class="probe"><span>Bas</span><strong data-role="tank_bottom">--</strong></div>
            </div>
            <div class="tank-label">Ballon d'eau chaude tampon</div>
          </section>
          <div class="pipe boiler-pipe"></div>
          <section class="source boiler">
            <h3><ha-icon icon="mdi:fire"></ha-icon>Poêle bouilleur</h3>
            <div class="reading"><span>Température</span><strong data-role="wood_boiler">--</strong></div>
            <div class="pumps" data-pumps="wood_boiler_pump"></div>
          </section>
        </div>
        <div class="warning" data-warning hidden></div>
      </ha-card>
    `;
  }

  setConfig(config) {
    if (
      config.controller_entity !== undefined &&
      typeof config.controller_entity !== "string"
    ) {
      throw new Error("controller_entity must be an entity ID");
    }
    this._title = config.title || "Ballon tampon";
    this._controllerEntity = config.controller_entity;
    if (this.shadowRoot) {
      this.shadowRoot.querySelector("[data-title]").textContent = this._title;
    }
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 6;
  }

  _roleSensors(role) {
    const matches = Object.values(this._hass.states).filter((state) =>
      (state.attributes.scc_roles || []).includes(role),
    );
    if (!this._controllerEntity) {
      return matches;
    }
    const controller = this._hass.states[this._controllerEntity];
    if (!controller?.attributes.scc_controller_id) {
      return [];
    }
    return matches.filter(
      (state) =>
        state.attributes.scc_controller_id ===
        controller.attributes.scc_controller_id,
    );
  }

  _temperature(role) {
    const matches = this._roleSensors(role);
    if (matches.length !== 1) {
      return { value: "--", ambiguous: matches.length > 1 };
    }
    const value = Number(matches[0].state);
    return {
      value: Number.isFinite(value) ? `${value.toFixed(1)} °C` : "--",
      ambiguous: false,
    };
  }

  _renderPumps(role, container) {
    const matches = this._roleSensors(role);
    container.replaceChildren();
    if (!matches.length) {
      const empty = document.createElement("span");
      empty.className = "empty";
      empty.textContent = "Aucune pompe configurée";
      container.append(empty);
      return;
    }

    for (const state of matches) {
      const value = Number(state.state);
      const pump = document.createElement("span");
      pump.className = `pump ${
        Number.isFinite(value) ? (value > 0 ? "active" : "") : "unknown"
      }`;
      const pumpName =
        state.attributes.friendly_name || state.entity_id.split(".")[1];
      const pumpStatus = Number.isFinite(value)
        ? value > 0
          ? "En marche"
          : "Arrêt"
        : "Indisponible";
      pump.textContent = `${pumpName} · ${pumpStatus}`;
      container.append(pump);
    }
  }

  _render() {
    if (!this._hass) {
      return;
    }
    let hasAmbiguousRole = false;
    for (const role of [
      "tank_top",
      "tank_middle",
      "tank_bottom",
      "solar_flow",
      "solar_return",
      "wood_boiler",
    ]) {
      const reading = this._temperature(role);
      this.shadowRoot.querySelector(`[data-role="${role}"]`).textContent =
        reading.value;
      hasAmbiguousRole ||= reading.ambiguous;
    }
    this._renderPumps(
      "solar_pump",
      this.shadowRoot.querySelector('[data-pumps="solar_pump"]'),
    );
    this._renderPumps(
      "wood_boiler_pump",
      this.shadowRoot.querySelector('[data-pumps="wood_boiler_pump"]'),
    );

    const warning = this.shadowRoot.querySelector("[data-warning]");
    warning.hidden = !hasAmbiguousRole;
    warning.textContent = hasAmbiguousRole
      ? "Plusieurs capteurs sont associés à un même rôle. Vérifiez la configuration de l'intégration."
      : "";
  }
}

customElements.define("scc-thermal-card", SccThermalCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "scc-thermal-card",
  name: "Chriselec SCC – Ballon tampon",
  description: "Visualisation du ballon tampon, du solaire et du poêle bouilleur.",
});
