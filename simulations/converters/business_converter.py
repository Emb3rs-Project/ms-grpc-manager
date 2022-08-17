from gis.gis_models import OptimizeNetworkOutputModel
from market.market_models import LongTermOutputModel
from teo.teo_models import BuildModelOutputModel


def platform_to_financial_feasability(initial_data):
    input_data = initial_data["input_data"]
    feasability = {
        "rls": input_data["rls"],
        "discountrate_i": input_data["discount_rate"],
        "projectduration": input_data["project_duration"],
        "actorshare": input_data["actorshare"],
        "co2_intensity": input_data["co2_intensity"]
    }
    return feasability


def gis_module_to_financial_feasability(river_data):
    river_optimize_network = OptimizeNetworkOutputModel().from_grpc(river_data["optimize_network"])
    feasability = {
        "net_cost": river_optimize_network.sums["total_costs"]
    }
    return feasability


def teo_module_to_financial_feasability(river_data):
    river_buildmodel = BuildModelOutputModel().from_grpc(river_data["buildmodel"])
    feasability = {
        "DiscountedCapitalInvestmentByTechnology": river_buildmodel.DiscountedCapitalInvestmentByTechnology,
        "DiscountedCapitalInvestmentByStorage": river_buildmodel.DiscountedCapitalInvestmentByStorage,
        "DiscountedSalvageValueByTechnology": river_buildmodel.DiscountedSalvageValueByTechnology,
        "DiscountedSalvageValueByStorage": river_buildmodel.DiscountedSalvageValueByStorage,
        "TotalDiscountedFixedOperatingCost": river_buildmodel.TotalDiscountedFixedOperatingCost,
    }
    return feasability


def market_module_to_financial_feasability(river_data):
    river_long_term = LongTermOutputModel().from_grpc(river_data["long_term"])
    feasability = {
        "shadow_price": river_long_term.shadow_price,
        "Pn": river_long_term.Pn,
        "agent_operational_cost": river_long_term.agent_operational_cost,
    }
    return feasability
