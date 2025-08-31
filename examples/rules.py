# import libs
from pyThermoLinkDB.utils import create_rules_from_str
from rich import print

#
RULES_YAML = """
ALL:
  DATA:
    critical-pressure: Pc
    critical-temperature: Tc
    acentric-factor: AcFa
    enthalpy-of-formation-ideal-gas: EnFo_IG
    gibbs-energy-of-formation-ideal-gas: GiEnFo_IG
    enthalpy-of-formation-liquid: EnFo_LIQ
    gibbs-energy-of-formation-liquid: GiEnFo_LIQ
    boiling-temperature: Tb
    melting-temperature: Tm
    sublimation-temperature: Ts
  EQUATIONS:
    vapor-pressure: VaPr
    ideal-gas-heat-capacity: Cp_IG
    liquid-heat-capacity: Cp_LIQ
    enthalpy-of-vaporization: EnVap
    enthalpy-of-fusion: EnFus
    enthalpy-of-sublimation: EnSub
"""

# convert
rules_dict = create_rules_from_str(RULES_YAML)
print(rules_dict['ALL'])
