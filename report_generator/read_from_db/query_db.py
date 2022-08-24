"""Read From DB."""
import os
import sqlite3

import pandas

from report_generator.config import load_config
from report_generator.excel_extraction.excel_to_sql import create_connection


def read_from_db(options: dict):

    config = load_config()
    dir_path = config["dir_path"]
    conn_path = os.path.join(dir_path, "data", "database", "species.db")
    print(conn_path)
    conn = create_connection(conn_path)
    query_options = get_query_options(options)
    query = build_query(query_options)
    results = query_db(conn, query)
    return results


def get_query_options(options: dict) -> dict:
    query_options = {}
    for key, value in options.items():
        key = key.strip("--")
        if value == "":
            value = None
        if value == ["", ""]:
            value = []
        s_args = ["new", "cli", "gui", "no-setup", "help", "version", "no-db"]
        if (key not in s_args) and (value is not None) and (len(value) != 0):
            query_options[key] = value
    return query_options


def build_query(params: dict):

    where_list = []
    having_str = ""
    for key, value in params.items():
        if key == "GeographicRegion":
            having_str = f"HAVING {key} LIKE '%{value}%'"
        else:
            where_list.append(build_where_statements(key, value))

    sql = f"""
    WITH species_comp as (
    SELECT
        *,
        species_id as species_comp_id
    FROM
        species
        JOIN genus ON species.genus_id = genus.genus_id
        JOIN family ON genus.family_id = family.family_id
        JOIN order_taxon ON family.order_id = order_taxon.order_id
    ),
    geo_location_species_full as(
    SELECT
        species_id as geo_species_id,
        continent_name || " " || country_name || " " || region_name as location_name
    FROM
        geo_location_species
        JOIN geo_location ON geo_location_species.geo_location_id = geo_location.geo_location_id
        JOIN country ON geo_location.country_id = country.country_id
        JOIN continent ON country.continent_id = continent.continent_id
    )
    SELECT
    order_taxon_name as 'Order',
    family_name as Family,
    genus_name as Genus,
    species_name_latin as Species,
    size_max_male as SVLMMx,
    size_max_female as SVLFMx,
    size_max_record as SVLMx,
    longevity as Longevity,
    nesting_site_desc as NestingSite,
    clutch_min as ClutchMin,
    clutch_max as ClutchMax,
    clutch_avg as Clutch,
    parity_mode_desc as ParityMode,
    egg_diameter as EggDiameter,
    activity_kind as Activity,
    micro_habitat_name as MicroHabitat,
    group_concat(location_name) as GeographicRegion,
    iucn_status as IUCN,
    pop_trend_status as PopTrend,
    range_size as RangeSize,
    elevation_min as ElevationMin,
    elevation_max as ElevationMax,
    elevation_avg as Elevation
    FROM
    species_comp
    LEFT JOIN geo_location_species_full ON species_comp.species_comp_id = geo_location_species_full.geo_species_id
    LEFT JOIN activity_species ON species_comp.species_comp_id = activity_species.species_id
    LEFT JOIN activity ON activity_species.activity_id = activity.activity_id
    LEFT JOIN iucn ON species_comp.iucn_id = iucn.iucn_id
    LEFT JOIN micro_habitat_species ON species_comp.species_comp_id = micro_habitat_species.species_id
    LEFT JOIN micro_habitat ON micro_habitat_species.micro_habitat_id = micro_habitat.micro_habitat_id
    LEFT JOIN nesting_site_species ON species_comp.species_comp_id = nesting_site_species.species_id
    LEFT JOIN nesting_site ON nesting_site_species.nesting_site_id = nesting_site.nesting_site_id
    LEFT JOIN parity_mode ON species_comp.parity_mode_id = parity_mode.parity_mode_id
    LEFT JOIN pop_trend ON species_comp.pop_trend_id = pop_trend.pop_trend_id
    """
    print(where_list)
    where_sql = "AND ".join(where_list)
    if len(where_sql) > 0:
        sql += "WHERE "
    sql += where_sql
    sql += """
    GROUP BY
    species_comp_id"""
    sql += "\n" + having_str
    sql += """
    ORDER BY
    species_comp_id ASC
    """
    print(sql)
    return sql


def build_where_statements(key: str, values):
    where = ""
    if isinstance(values, list):
        if len(values) == 2 and all(x.isdigit() for x in values):
            print(values)
            # values = [int(x) for x in values].sort()
            where = f"{key} BETWEEN {values[0]} AND {values[1]}"
        elif len(values) > 2:
            ors = []
            for val in values:
                ors.append(f"{key} = {val}")
            where = "OR ".join(ors)
        else:
            where = f"{key} like '{values[0]}'"
    elif values.isdigit():
        where = f"{key} = {values}"
    else:
        where = f"{key} like '%{values}%'"
    return where


def query_db(conn: sqlite3.Connection, query: str) -> pandas.DataFrame:
    data_frame = pandas.read_sql_query(query, conn)
    print(data_frame.head())
    print(len(data_frame.index))
    return data_frame