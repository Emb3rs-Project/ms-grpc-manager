def cf_module_to_buildmodel(river_data):
    pass


def gis_module_to_buildmodel(river_data):
    return {"losses_in_kw": 347.70490750000005, "cost_in_kw": 15.832943848591178}


def platform_to_buildmodel(initial_data, river_data):

    return {
        "platform_sets": {
            "REGION": ["sweden"],
            "EMISSION": ["co2"],
            "TIMESLICE": [
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31,
                32,
                33,
                34,
                35,
                36,
                37,
                38,
                39,
                40,
                41,
                42,
                43,
                44,
                45,
                46,
                47,
                48,
            ],
            "YEAR": [2022],
            "MODE_OF_OPERATION": [1, 2],
            "STORAGE": ["sto1"],
        },
        "platform_storages": [
            {
                "storage": "sto1",
                "capital_cost_storage": 10,
                "dicount_rate_sto": 0.1,
                "operational_life_sto": 100,
                "storage_max_charge": 10000,
                "storage_max_discharge": 10000,
                "l2d": 1,
                "tag_heating": 1,
                "tag_cooling": 0,
                "storage_return_temp": 50,
                "storage_supply_temp": 80,
                "storage_ambient_temp": 20,
                "residual_storage_capacity": 0,
                "max_storage_capacity": 45000,
                "storage_level_start": 10,
                "u_value": 0.14,
            },
            {
                "storage": "sto2",
                "capital_cost_storage": 10,
                "dicount_rate_sto": 0.1,
                "operational_life_sto": 100,
                "storage_max_charge": 10000,
                "storage_max_discharge": 10000,
                "l2d": 1,
                "tag_heating": 1,
                "tag_cooling": 0,
                "storage_return_temp": 50,
                "storage_supply_temp": 80,
                "storage_ambient_temp": 20,
                "residual_storage_capacity": 0,
                "max_storage_capacity": 4500,
                "storage_level_start": 10,
                "u_value": 0,
            },
        ],
        "platform_annual_emission_limit": [
            {"emission": "co2", "annual_emission_limit": 15000000}
        ],
        "platform_budget_limit": [{"Region": "Sweden", "budget_limit": 1}],
        "platform_technology_to_storage": [
            {
                "technology": "dhn",
                "storage": "sto1",
                "technologytostorage": 1,
                "technologyfromstorage": 1,
            },
            {
                "technology": "sink1str2shex",
                "storage": "sto2",
                "technologytostorage": 1,
                "technologyfromstorage": 1,
            },
        ],
    }
