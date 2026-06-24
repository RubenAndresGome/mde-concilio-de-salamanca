from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


BIG_MAC_INDEX: Dict[str, float] = {
    "US": 5.69,
    "CH": 7.73,
    "NO": 7.14,
    "SE": 5.84,
    "DK": 5.67,
    "IL": 5.34,
    "CA": 5.27,
    "AU": 5.07,
    "NZ": 4.88,
    "GB": 4.82,
    "KR": 4.43,
    "AE": 4.39,
    "JP": 4.35,
    "DE": 4.25,
    "FR": 4.20,
    "IT": 4.15,
    "ES": 3.95,
    "PT": 3.72,
    "GR": 3.68,
    "PL": 3.45,
    "CZ": 3.42,
    "HU": 3.35,
    "RO": 3.28,
    "CL": 3.75,
    "BR": 4.25,
    "AR": 3.15,
    "CO": 3.48,
    "PE": 3.25,
    "MX": 3.19,
    "CR": 4.10,
    "PA": 3.90,
    "DO": 3.55,
    "GT": 3.50,
    "EC": 3.40,
    "PY": 3.30,
    "BO": 3.20,
    "UY": 4.80,
    "ZA": 3.10,
    "EG": 2.55,
    "NG": 2.40,
    "KE": 2.30,
    "ET": 2.10,
    "IN": 2.39,
    "CN": 3.25,
    "TH": 3.05,
    "VN": 2.85,
    "ID": 2.55,
    "PH": 2.60,
    "PK": 2.10,
    "BD": 2.05,
    "MM": 2.00,
    "RU": 2.95,
    "TR": 2.80,
    "UA": 2.15,
    "SG": 4.90,
    "HK": 4.85,
    "TW": 4.40,
    "MY": 2.85,
}

RENT_RATIO: Dict[str, float] = {
    "US": 0.35, "CH": 0.38, "NO": 0.35, "SE": 0.33, "DK": 0.34,
    "GB": 0.36, "DE": 0.32, "FR": 0.30, "IT": 0.28, "ES": 0.30,
    "PT": 0.28, "GR": 0.26, "PL": 0.28, "CZ": 0.30, "HU": 0.26,
    "RO": 0.24, "AU": 0.33, "NZ": 0.32, "CA": 0.34, "JP": 0.30,
    "KR": 0.28, "SG": 0.32, "HK": 0.38, "TW": 0.26, "CN": 0.28,
    "IN": 0.22, "BR": 0.25, "MX": 0.24, "AR": 0.26, "CO": 0.24,
    "CL": 0.24, "PE": 0.22, "ZA": 0.23, "NG": 0.30, "KE": 0.28,
    "EG": 0.24, "TH": 0.22, "VN": 0.20, "ID": 0.22, "PH": 0.25,
    "PK": 0.20, "BD": 0.18, "TR": 0.24, "RU": 0.22, "UA": 0.20,
}

FOOD_RATIO: Dict[str, float] = {
    "US": 0.12, "CH": 0.14, "NO": 0.13, "SE": 0.12, "DK": 0.12,
    "GB": 0.11, "DE": 0.11, "FR": 0.13, "IT": 0.13, "ES": 0.12,
    "PT": 0.13, "GR": 0.12, "PL": 0.15, "CZ": 0.14, "HU": 0.14,
    "RO": 0.16, "AU": 0.11, "NZ": 0.12, "CA": 0.11, "JP": 0.12,
    "KR": 0.12, "SG": 0.11, "HK": 0.12, "TW": 0.11, "CN": 0.15,
    "IN": 0.18, "BR": 0.14, "MX": 0.15, "AR": 0.16, "CO": 0.15,
    "CL": 0.14, "PE": 0.16, "ZA": 0.14, "NG": 0.25, "KE": 0.24,
    "EG": 0.18, "TH": 0.16, "VN": 0.18, "ID": 0.18, "PH": 0.20,
    "PK": 0.20, "BD": 0.22, "TR": 0.16, "RU": 0.16, "UA": 0.18,
}

TAX_ESTIMATES: Dict[str, float] = {
    "US": 0.24, "CH": 0.22, "NO": 0.30, "SE": 0.32, "DK": 0.36,
    "GB": 0.25, "DE": 0.30, "FR": 0.28, "IT": 0.30, "ES": 0.24,
    "PT": 0.25, "GR": 0.24, "PL": 0.18, "CZ": 0.16, "HU": 0.15,
    "RO": 0.10, "AU": 0.27, "NZ": 0.24, "CA": 0.26, "JP": 0.23,
    "KR": 0.17, "SG": 0.10, "HK": 0.10, "TW": 0.12, "CN": 0.15,
    "IN": 0.13, "BR": 0.17, "MX": 0.16, "AR": 0.20, "CO": 0.15,
    "CL": 0.15, "PE": 0.12, "ZA": 0.22, "NG": 0.10, "KE": 0.14,
    "EG": 0.10, "TH": 0.10, "VN": 0.10, "ID": 0.10, "PH": 0.10,
    "PK": 0.05, "BD": 0.07, "TR": 0.15, "RU": 0.13, "UA": 0.12,
}

DEFAULT_BIG_MAC = 3.50
DEFAULT_RENT = 0.30
DEFAULT_FOOD = 0.14
DEFAULT_TAX = 0.15

BME_BRACKETS = [
    (500, 0.00, "Gratis (solo Auto-Favorito)"),
    (2000, 0.01, "1% del ingreso bruto atribuible"),
    (5000, 0.03, "3% del ingreso bruto atribuible"),
    (10000, 0.05, "5% del ingreso bruto atribuible"),
    (float("inf"), 0.10, "10% del ingreso bruto atribuible"),
]


class BigMacCalculator:
    @staticmethod
    def big_mac_price(country: str) -> float:
        return BIG_MAC_INDEX.get(country.upper(), DEFAULT_BIG_MAC)

    @staticmethod
    def disposable_income_bme(
        monthly_income_usd: float,
        residence_country: str,
        income_country: Optional[str] = None,
    ) -> float:
        res = residence_country.upper()
        big_mac = BigMacCalculator.big_mac_price(res)
        rent_r = RENT_RATIO.get(res, DEFAULT_RENT)
        food_r = FOOD_RATIO.get(res, DEFAULT_FOOD)
        tax_r = TAX_ESTIMATES.get(res, DEFAULT_TAX)

        costs = monthly_income_usd * (rent_r + food_r + tax_r)
        disposable = max(monthly_income_usd - costs, 0)
        return disposable / big_mac if big_mac > 0 else 0

    @staticmethod
    def get_tax_bracket(bme: float) -> tuple:
        for threshold, rate, label in BME_BRACKETS:
            if bme < threshold:
                return (rate, label, bme)
        return (0.10, BME_BRACKETS[-1][2], bme)


class LicenseGenerator:
    BASE_THRESHOLD_USD = 1_000_000
    BASE_SME_THRESHOLD_USD = 250_000
    BASE_NONPROFIT_THRESHOLD_USD = 100_000
    POOR_DEV_THRESHOLD_MXN = 20_000

    def __init__(self, developer_name: str = "", project_name: str = "",
                 github_repo: str = ""):
        self.developer_name = developer_name
        self.project_name = project_name
        self.github_repo = github_repo

    def get_localized_thresholds(self, country_code: str) -> Dict:
        factor = 1.0
        if country_code.upper() in BIG_MAC_INDEX:
            factor = BIG_MAC_INDEX[country_code.upper()] / BIG_MAC_INDEX.get("US", 5.69)
        factor = max(factor, 0.3)

        bm_price_usd = BIG_MAC_INDEX.get(country_code.upper(), DEFAULT_BIG_MAC)
        poor_dev_usd = (self.POOR_DEV_THRESHOLD_MXN / 55) * (bm_price_usd / BIG_MAC_INDEX.get("MX", 3.19))

        bme_brackets_display = []
        for threshold, rate, label in BME_BRACKETS:
            bme_in_usd = threshold * bm_price_usd
            bme_brackets_display.append({
                "bme": threshold,
                "tasa": f"{rate*100:.0f}%",
                "equivalente_usd_mensual": f"${bme_in_usd:,.0f}",
                "label": label,
            })

        return {
            "ingresos_brutos_alto": self.BASE_THRESHOLD_USD * factor,
            "ingresos_brutos_pyme": self.BASE_SME_THRESHOLD_USD * factor,
            "nonprofit_max": self.BASE_NONPROFIT_THRESHOLD_USD * factor,
            "poor_dev_usd": poor_dev_usd,
            "big_mac_price_usd": bm_price_usd,
            "bme_brackets": bme_brackets_display,
            "ppa_factor": factor,
        }

    def generate_license(self, country_code: str = "US") -> str:
        t = self.get_localized_thresholds(country_code)
        bm_price = t["big_mac_price_usd"]
        brackets = t["bme_brackets"]

        brackets_text = ""
        for b in brackets:
            brackets_text += (
                f"  - Hasta {b['bme']} BME (~${b['equivalente_usd_mensual']}/mes "
                f"en {country_code.upper()}): **{b['label']}**\n"
            )

        return f"""# LICENCIA PUBLICA RERUM NOVARUM (LPRN) v2.0
## Promulgada bajo los principios del Derecho Natural y la Economia Fisica
### Sistema de Precio Justo: Indice Big Mac (BMI)
### Adaptada para: {country_code.upper()} (Big Mac local: ${bm_price:.2f} USD)

**Preambulo: De la Naturaleza del Trabajo y el Septimo Mandamiento**

El codigo de *software* no es una abstraccion eterea; es el producto directo del tiempo,
el intelecto y el consumo calorico de un trabajador humano. Por tanto, esta sujeto a la
Ley Natural y a la Doctrina del Precio Justo.

Extraer ganancia economica del trabajo de otro sin otorgar la retribucion proporcional
constituye un acto de usura y una violacion directa al Septimo Mandamiento del Decalogo
("No robaras"). Ningun contrato fiduciario, terminos de servicio o laguna legal puede
alterar la realidad ontologica de que **el robo es robo**.

Esta licencia no es solo un contrato: es un **acto de Justicia Distributiva**.

---

### 1. Definiciones

- **"Software"**: El programa, biblioteca o codigo objeto de esta licencia, incluyendo
  codigo fuente y binarios.
- **"Desarrollador"**: {self.developer_name or '[Nombre del desarrollador]'}, titular
  de los derechos de autor del Software.
- **"Proyecto"**: {self.project_name or '[Nombre del proyecto]'}.
- **"Usuario"**: Cualquier persona o entidad que use, modifique o distribuya el Software.
- **"Big Mac Equivalent (BME)"**: Unidad de medida del poder adquisitivo real. Un BME
  equivale al precio de una Big Mac en el pais de residencia del Usuario.
  Precio de referencia en {country_code.upper()}: ${bm_price:.2f} USD = 1 BME.
- **"Ingreso Disponible Mensual"**: Ingreso bruto mensual del Usuario, menos:
  - Renta promedio local (~{RENT_RATIO.get(country_code.upper(), 0.30)*100:.0f}% del ingreso en {country_code.upper()})
  - Alimentacion basica (~{FOOD_RATIO.get(country_code.upper(), 0.14)*100:.0f}% del ingreso en {country_code.upper()})
  - Impuestos estimados (~{TAX_ESTIMATES.get(country_code.upper(), 0.15)*100:.0f}% del ingreso en {country_code.upper()})
- **"Ingresos Brutos del Software"**: La suma total de dinero o valor monetizable recibida
  directamente por la venta, licenciamiento, suscripciones, servicios asociados o
  publicidad vinculada al Software, antes de impuestos.
- **"PYME"**: Empresa con menos de 100 empleados y facturacion anual inferior a
  ${t['ingresos_brutos_pyme']:,.0f} USD (ajustado segun PPA local).
- **"Economia Fisica"**: Produccion de bienes y servicios reales (manufactura, agricultura,
  logistica, infraestructura).
- **"Economia Fiduciaria"**: Especulacion financiera, banca de inversion, fondos de
  cobertura, seguros y derivados.

### 2. Libertades Concedidas

Se permite, sin cargo inicial, a cualquier Usuario:
a) Ejecutar el Software para cualquier proposito.
b) Estudiar y modificar el codigo fuente.
c) Distribuir copias literales o modificadas, siempre que se mantenga esta misma licencia
   y se cumplan las condiciones de retribucion del Articulo 3.

### 3. El Uso Asimetrico (La Ley de la Sustancia)

**3.1 Acceso Libre y Gratuito**
El Software es de uso irrestricto, gratuito y perpetuo para:
- Individuos y estudiantes.
- Desarrolladores independientes cuyo Ingreso Disponible Mensual sea inferior a
  500 BME (~${t['poor_dev_usd']:,.0f} USD en {country_code.upper()}, equivalente a
  {self.POOR_DEV_THRESHOLD_MXN:,} MXN en Mexico). Si tu ingreso disponible no alcanza
  para 500 Big Macs al mes, este codigo es tuyo, gratis, sin condicion economica alguna.
  Solo se te pide el Auto-Favorito (Articulo 3.4).
- Proyectos de codigo abierto (open source) bajo cualquier licencia aprobada por la OSI
  o la FSF, siempre que el proyecto no cobre por el uso del Software en si.
- Conocimiento y skills: esta licencia reconoce que el conocimiento es GNU por naturaleza.
  Si eres estudiante, investigador o estas aprendiendo, el pago es el Auto-Favorito.
- Instituciones educativas y organizaciones sin animo de lucro con presupuesto inferior
  a ${t['nonprofit_max']:,.0f} USD anuales.
- Cooperativas y proyectos de infraestructura publica.
- Empresas de economia fisica cuyos ingresos brutos anuales no superen
  ${t['ingresos_brutos_alto']:,.0f} USD.
- Entidades gubernamentales de paises con IDH inferior a 0.6 (si no se usa para generar
  ingresos directos).

**3.2 Clausula de Geo-Arbitraje (El Gringo en la Playa)**
Si el Usuario reside en un pais de bajo costo de vida (ej. Mexico, Colombia, Tailandia)
pero percibe ingresos de un pais de alto costo (ej. Estados Unidos, Suiza, Noruega), el
calculo del Ingreso Disponible en BME se realizara usando el precio de Big Mac del pais
de residencia Y el ingreso del pais de origen. Esto garantiza que quien goza de arbitraje
geografico pague la tasa que corresponde a su capacidad real de compra, no a la del pais
donde finge ser pobre.

*Ejemplo:* Un desarrollador ganando $8,000 USD/mes de una empresa en California pero
viviendo en Oaxaca (Big Mac MX = $3.19) tiene un poder adquisitivo de ~2,000 BME/mes
(despues de costos locales), lo que lo coloca en el tramo del 3%, no en el gratuito.

**3.3 El Peaje Corporativo (Entidades Fiduciarias)**
Toda entidad financiera, corporacion bancaria, fondo de cobertura, aseguradora, o
corporacion de *Big Tech* que utilice este codigo para generar lucro fiduciario NO posee
licencia gratuita. El uso del Software por estas entidades genera automaticamente una
deuda de Restitucion Material del 10% fijo.

**3.4 Auto-Favorito en GitHub (Clausula del Diezmo Digital Minimo)**
Todo Usuario que se beneficie del Software, sin importar su categoria de ingreso,
reconoce la deuda moral de retribuir aunque sea en la moneda mas barata del ecosistema:
el *star* en GitHub.
- Si el Proyecto esta alojado en GitHub{f' ({self.github_repo})' if self.github_repo else ''},
  el Usuario se compromete, bajo palabra de desarrollador, a darle *Star* (favorito) al
  repositorio.
- Este acto no es opcional: es el reconocimiento minimo de que el trabajo ajeno tiene
  valor. Cuesta cero dolares, un clic, y salda la deuda de gratitud.
- Los servidores de GitHub registran este acto. La omision del Auto-Favorito no invalida
  la licencia, pero deja al Usuario en estado de "deuda moral no saldada" ante el
  tribunal silencioso del open source.
- Compartir el repo, dar fork, o mencionarlo en redes sociales son actos de restitucion
  adicional voluntaria pero altamente recomendados por el Magister.

### 4. Deber de Retribucion ("Diezmo Tecnologico") - Sistema Big Mac

La tasa de retribucion se determina segun el Ingreso Disponible Mensual del Usuario
expresado en BME (Big Mac Equivalents). El Usuario debe autoevaluar su categoria y
aplicar la tasa correspondiente sobre los Ingresos Brutos del Software.

**Escala Impositiva Universal (1% a 10%):**

{brackets_text}

**4.1 Pago en codigo o en licencia**
Para ingresos brutos anuales del Software inferiores a
${t['ingresos_brutos_alto']:,.0f} USD, el Usuario podra optar por:
- Contribuir codigo aprobado al proyecto original (al menos 5% del esfuerzo total de
  desarrollo), o
- Abonar el porcentaje correspondiente segun su BME.

**4.2 Tramo corporativo**
Para ingresos brutos anuales del Software iguales o superiores a
${t['ingresos_brutos_alto']:,.0f} USD, el Usuario abonara el porcentaje de su tramo BME,
con un minimo del 5%.

**4.3 Modelo WinRAR para PYMEs**
Las PYMEs podran utilizar el Software gratuitamente durante los primeros 18 meses.
Transcurrido ese periodo, si la PYME ha superado los
${t['ingresos_brutos_pyme']:,.0f} USD de ingresos anuales vinculados, debera
comprar una licencia de uso comercial o acogerse al plan de "credito al desarrollo".

### 5. Clausula Anti-Parasitaria

Toda entidad cuyo modelo de negocio principal sea la especulacion fiduciaria o la
extraccion de rentas sobre deuda NO posee licencia gratuita. Si una corporacion de
Big Tech o entidad financiera integra este trabajo en un servicio comercial, el uso
de este material constituye una deuda de Restitucion Material del 10% fijo.

### 6. Retroactividad de la Verdad (Clausula Parmenidea)

La verdad es inmutable y no esta sujeta a la linealidad del tiempo ni a la prescripcion
de tribunales fiduciarios. Si una accion es un robo hoy bajo la Ley Natural, tambien lo
fue ayer. Esta licencia es **estrictamente retroactiva**: si una corporacion es descubierta
utilizando este codigo sin haber compensado a sus creadores, la deuda se calcula desde el
primer ciclo de procesamiento en que se ejecuto el software con fines de lucro.

### 7. Excomunion Digital

La violacion de los terminos de esta licencia resultara en la "Excomunion Digital":
denegacion de licencias futuras, orden de purga del codigo de los servidores de la
entidad infractora, y bloqueo de ejecucion en red. Lo que la corporacion se niega a
pagar, el codigo se niega a compilar.

### 8. Compatibilidad

Esta licencia no es compatible con GPL ni Creative Commons estandar en tanto no se
respete el capitulo de retribucion. Cualquier obra derivada debe mantenerse bajo esta
misma licencia. Sin embargo, el conocimiento y las skills derivadas del Software se
rigen por el principio GNU: el conocimiento es libre; lo que se licencia aqui es la
implementacion material, no la idea.

### 9. Garantia y Limitacion de Responsabilidad

EL SOFTWARE SE PROPORCIONA "TAL CUAL", SIN GARANTIA DE NINGUN TIPO. EL DESARROLLADOR
NO SERA RESPONSABLE DE DANOS DIRECTOS O INDIRECTOS. EL UNICO VINCULO LEGAL ES LA JUSTA
RETRIBUCIÓN, CUYO INCUMPLIMIENTO GENERARA UNA DEUDA EXIGIBLE POR VIA CIVIL.

### 10. Disposiciones Finales

- Si algun tribunal considerase inaplicable alguna clausula, se sustituira por la maxima
  retribucion permitida por la ley, preservando el espiritu de la *Rerum Novarum*.
- El Desarrollador se compromete a destinar al menos el 20% de las regalias recibidas
  al Fondo de Solidaridad Leonino para sostener a otros desarrolladores bajo esta licencia.
- Esta licencia reconoce que la tecnologia debe servir al Bien Comun y a la prosperidad
  material de las naciones, prohibiendo su secuestro por entidades de especulacion
  financiera y monopolios nominalistas.

---

*Licencia generada el {datetime.now().strftime('%Y-%m-%d')} para {country_code.upper()}.
Redactada bajo el espiritu de la Meta Dialectica Escolastica (MDE), en la ciudad virtual
de Salamanca, por el Magister Determinans del Concilio.*

[![License: Rerum Novarum 2.0](https://img.shields.io/badge/License-Rerum_Novarum_2.0-purple.svg)](LICENSE.md)
"""

    def save_license(self, path: str, country_code: str = "US"):
        content = self.generate_license(country_code)
        Path(path).write_text(content, encoding="utf-8")
        return path

    @classmethod
    def list_countries(cls):
        return sorted(BIG_MAC_INDEX.keys())

    @classmethod
    def calculate_bme(cls, monthly_income_usd: float,
                      residence_country: str,
                      income_country: Optional[str] = None) -> dict:
        bme = BigMacCalculator.disposable_income_bme(
            monthly_income_usd, residence_country, income_country
        )
        rate, label, _ = BigMacCalculator.get_tax_bracket(bme)
        return {
            "bme": round(bme, 1),
            "tasa": f"{rate*100:.0f}%",
            "categoria": label,
            "big_mac_precio": BigMacCalculator.big_mac_price(residence_country),
        }
