"""Staví dotaz na DB, s příslušnými filtry"""


def build_query(query_template, min_date, species_name, square, limit=None):
    """Sestaví dotaz"""
    where_clause = ""

    if not (min_date is not None or species_name is not None):
        return query_template.format(conditions="")

    where_clause = "WHERE "
    clause_conds = []
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

    where_clause += " AND ".join(clause_conds) + (
        f" LIMIT {limit}" if limit is not None else ""
    )

    return query_template.format(conditions=where_clause)
