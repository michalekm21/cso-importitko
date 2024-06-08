"""Sestaví dotaz na DB, s příslušnými filtry"""
import utils.lib.yaml as yaml


def build_query(min_date, species_name, square, limit, user):
    """Sestaví dotaz"""
    where_clause = ""
    clause_conds = []

    with open('query.yaml', 'r', encoding="utf-8") as file:
        query_yaml = yaml.safe_load(file)
        if user is not None:
            query_template = query_yaml['template_user']
            clause_conds.append(
                f"((LOWER(Observer) RLIKE LOWER('%{user}%')) OR"
                f" (LOWER(ObserversEmail) RLIKE LOWER('%{user}%')))")

        else:
            query_template = query_yaml['template_no_user']

    if min_date is not None:
        date_string = min_date if len(min_date) != 4 else min_date + '-1-1'
        clause_conds.append(f"(ObsDate >= '{date_string}')")
    if species_name is not None:
        clause_conds.append(
            f"((LOWER(NameCS) LIKE LOWER('%{species_name}%')) OR"
            f" (LOWER(NameLA) LIKE LOWER('%{species_name}%')))")
    if square is not None:
        clause_conds.append(
            f"((SUBSTRING(SiteName, 1, 6) RLIKE '{square}') > 0)")

    if clause_conds:
        where_clause = "WHERE " + " AND ".join(clause_conds)

    where_clause += f" LIMIT {limit}" if limit is not None else ""

    return query_template.format(conditions=where_clause)
