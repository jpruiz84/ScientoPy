import sqlite3
import csv
import os
import re
import globalVar


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_PAPERS_SCHEMA = """
CREATE TABLE IF NOT EXISTS papers (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    eid                     TEXT NOT NULL UNIQUE,
    doi                     TEXT DEFAULT '',
    title                   TEXT NOT NULL,
    titleNorm               TEXT DEFAULT '',
    firstAuthorNorm         TEXT DEFAULT '',

    author                  TEXT DEFAULT '',
    authorFull              TEXT DEFAULT '',
    year                    INTEGER,
    sourceTitle             TEXT DEFAULT '',
    citedBy                 INTEGER DEFAULT 0,

    volume                  TEXT DEFAULT '',
    issue                   TEXT DEFAULT '',
    artNo                   TEXT DEFAULT '',
    pageStart               TEXT DEFAULT '',
    pageEnd                 TEXT DEFAULT '',
    pageCount               TEXT DEFAULT '',
    link                    TEXT DEFAULT '',
    publisher               TEXT DEFAULT '',
    issn                    TEXT DEFAULT '',
    isbn                    TEXT DEFAULT '',

    abstract                TEXT DEFAULT '',
    authorKeywords          TEXT DEFAULT '',
    indexKeywords            TEXT DEFAULT '',
    bothKeywords            TEXT DEFAULT '',
    subject                 TEXT DEFAULT '',
    documentType            TEXT DEFAULT '',
    dataBase                TEXT DEFAULT '',

    affiliations            TEXT DEFAULT '',
    authorsWithAffiliations TEXT DEFAULT '',
    country                 TEXT DEFAULT '',
    institution             TEXT DEFAULT '',
    institutionWithCountry  TEXT DEFAULT '',
    correspondenceAddress   TEXT DEFAULT '',
    emailHost               TEXT DEFAULT '',

    duplicatedIn            TEXT DEFAULT '',

    source                  TEXT DEFAULT '',
    cr                      TEXT DEFAULT '',
    orcid                   TEXT DEFAULT '',
    citedReferences         TEXT DEFAULT '',
    publisherAddress        TEXT DEFAULT '',
    conferenceTitle         TEXT DEFAULT '',
    conferenceLocation      TEXT DEFAULT '',
    conferenceDate          TEXT DEFAULT '',
    editors                 TEXT DEFAULT '',
    coden                   TEXT DEFAULT '',
    pubMedId                TEXT DEFAULT '',
    languageOfOriginalDocument TEXT DEFAULT '',
    abbreviatedSourceTitle  TEXT DEFAULT '',
    countries               TEXT DEFAULT '',
    author_ids              TEXT DEFAULT '',

    importedAt              TEXT DEFAULT (datetime('now'))
);
"""

_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_papers_dedup ON papers (titleNorm, firstAuthorNorm);",
    "CREATE INDEX IF NOT EXISTS idx_papers_doi ON papers (doi) WHERE doi != '';",
    "CREATE INDEX IF NOT EXISTS idx_papers_year ON papers (year);",
    "CREATE INDEX IF NOT EXISTS idx_papers_dataBase ON papers (dataBase);",
    "CREATE INDEX IF NOT EXISTS idx_papers_documentType ON papers (documentType);",
    "CREATE INDEX IF NOT EXISTS idx_papers_eid ON papers (eid);",
]

_KEYWORDS_SCHEMA = """
CREATE TABLE IF NOT EXISTS keywords (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id  INTEGER NOT NULL REFERENCES papers(id),
    field     TEXT NOT NULL,
    keyword   TEXT NOT NULL,
    position  INTEGER DEFAULT 0,
    UNIQUE(paper_id, field, keyword, position)
);
"""

_KEYWORDS_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_keywords_lookup ON keywords (field, keyword);",
    "CREATE INDEX IF NOT EXISTS idx_keywords_paper ON keywords (paper_id);",
]

# Fields that get split into the keywords table
KEYWORD_FIELDS = [
    'authorKeywords', 'indexKeywords', 'bothKeywords',
    'country', 'institution', 'institutionWithCountry',
    'subject', 'author', 'sourceTitle', 'documentType', 'dataBase',
    'abstract',
]


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

def init_db(conn):
    cur = conn.cursor()
    cur.executescript(_PAPERS_SCHEMA)
    for idx_sql in _INDEXES:
        cur.execute(idx_sql)
    cur.executescript(_KEYWORDS_SCHEMA)
    for idx_sql in _KEYWORDS_INDEXES:
        cur.execute(idx_sql)
    conn.commit()


def get_connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn


# ---------------------------------------------------------------------------
# Column mapping  (paper dict <-> DB row)
# ---------------------------------------------------------------------------

# All columns in the papers table (minus id, importedAt which are auto)
_PAPER_COLUMNS = [
    'eid', 'doi', 'title', 'titleNorm', 'firstAuthorNorm',
    'author', 'authorFull', 'year', 'sourceTitle', 'citedBy',
    'volume', 'issue', 'artNo', 'pageStart', 'pageEnd', 'pageCount',
    'link', 'publisher', 'issn', 'isbn',
    'abstract', 'authorKeywords', 'indexKeywords', 'bothKeywords',
    'subject', 'documentType', 'dataBase',
    'affiliations', 'authorsWithAffiliations',
    'country', 'institution', 'institutionWithCountry',
    'correspondenceAddress', 'emailHost',
    'duplicatedIn',
    'source', 'cr', 'orcid', 'citedReferences',
    'publisherAddress', 'conferenceTitle', 'conferenceLocation', 'conferenceDate',
    'editors', 'coden', 'pubMedId', 'languageOfOriginalDocument',
    'abbreviatedSourceTitle', 'countries', 'author_ids',
]

# Maps DB column -> legacy dict key (only where they differ)
_DB_TO_DICT = {
    'pageStart': 'pageSart',  # preserve legacy typo
}

# Maps legacy dict key -> DB column (only where they differ)
_DICT_TO_DB = {v: k for k, v in _DB_TO_DICT.items()}


def paper_dict_to_row(d):
    """Convert a legacy paper dict to a tuple matching _PAPER_COLUMNS."""
    import unidecode as _unidecode

    row = []
    for col in _PAPER_COLUMNS:
        dict_key = _DB_TO_DICT.get(col, col)
        val = d.get(dict_key, d.get(col, ''))

        if col == 'year':
            if isinstance(val, str) and val.isdigit():
                val = int(val)
            elif isinstance(val, int):
                pass
            else:
                val = None
        elif col == 'citedBy':
            if isinstance(val, str):
                val = int(val) if val.isdigit() else 0
            elif isinstance(val, (int, float)):
                val = int(val)
            else:
                val = 0
        elif col == 'duplicatedIn':
            if isinstance(val, list):
                val = ';'.join(val)
            elif val is None:
                val = ''
        elif col == 'titleNorm':
            title = d.get('title', '')
            val = _unidecode.unidecode(title)
            val = re.sub(r'[\(\[].*?[\)\]]', '', val.upper()).strip()
            val = re.sub(r'[^a-zA-Z0-9]+', '', val)
        elif col == 'firstAuthorNorm':
            author = d.get('author', '')
            val = _unidecode.unidecode(author).upper().strip()
            val = re.sub(r';|\.|,', ' ', val).split(' ')[0]
            val = re.sub(r'[^a-zA-Z]+', '', val)
        else:
            if val is None:
                val = ''

        row.append(val)
    return tuple(row)


def row_to_paper_dict(row):
    """Convert a DB row (sqlite3.Row) to a legacy paper dict."""
    d = {}
    for col in _PAPER_COLUMNS:
        dict_key = _DB_TO_DICT.get(col, col)
        val = row[col] if row[col] is not None else ''

        if col == 'year':
            d[dict_key] = str(val) if val is not None else ''
        elif col == 'citedBy':
            d[dict_key] = val if isinstance(val, int) else 0
        elif col == 'duplicatedIn':
            if isinstance(val, str) and val:
                d[dict_key] = val.split(';')
            else:
                d[dict_key] = []
        elif col == 'titleNorm' or col == 'firstAuthorNorm':
            continue  # not in legacy dict
        else:
            d[dict_key] = str(val)

    # Legacy compat: also provide pageStart as 'pageSart'
    # (already handled by _DB_TO_DICT)
    return d


# ---------------------------------------------------------------------------
# Bulk insert
# ---------------------------------------------------------------------------

_INSERT_SQL = (
    "INSERT OR IGNORE INTO papers ({cols}) VALUES ({placeholders})"
    .format(
        cols=', '.join(_PAPER_COLUMNS),
        placeholders=', '.join(['?'] * len(_PAPER_COLUMNS)),
    )
)


def insert_papers_bulk(conn, paper_dicts):
    """Batch-insert paper dicts into the DB. Returns number of rows inserted."""
    cur = conn.cursor()
    rows = [paper_dict_to_row(d) for d in paper_dicts]
    cur.executemany(_INSERT_SQL, rows)
    conn.commit()
    return cur.rowcount


def insert_paper_get_id(conn, paper_dict):
    """Insert a single paper and return its rowid. Returns None if duplicate eid."""
    cur = conn.cursor()
    row = paper_dict_to_row(paper_dict)
    try:
        cur.execute(_INSERT_SQL, row)
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None


# ---------------------------------------------------------------------------
# Keywords table population
# ---------------------------------------------------------------------------

def populate_keywords_for_paper(conn, paper_id, paper_dict):
    """Split semicolon-delimited fields and insert into keywords table."""
    cur = conn.cursor()
    for field in KEYWORD_FIELDS:
        dict_key = _DB_TO_DICT.get(field, field)
        value = paper_dict.get(dict_key, paper_dict.get(field, ''))
        if not value:
            continue
        for i, kw in enumerate(str(value).split(';')):
            kw = kw.strip()
            if not kw:
                continue
            try:
                cur.execute(
                    "INSERT OR IGNORE INTO keywords (paper_id, field, keyword, position) VALUES (?,?,?,?)",
                    (paper_id, field, kw.upper(), i)
                )
            except sqlite3.IntegrityError:
                pass


def populate_all_keywords(conn):
    """Populate keywords table from all papers in the DB."""
    cur = conn.cursor()
    cur.execute("DELETE FROM keywords")
    papers = cur.execute("SELECT * FROM papers").fetchall()
    for paper_row in papers:
        paper_id = paper_row['id']
        for field in KEYWORD_FIELDS:
            value = paper_row[field] if paper_row[field] else ''
            if not value:
                continue
            for i, kw in enumerate(str(value).split(';')):
                kw = kw.strip()
                if not kw:
                    continue
                try:
                    cur.execute(
                        "INSERT OR IGNORE INTO keywords (paper_id, field, keyword, position) VALUES (?,?,?,?)",
                        (paper_id, field, kw.upper(), i)
                    )
                except sqlite3.IntegrityError:
                    pass
    conn.commit()


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

def get_all_papers(conn, start_year=None, end_year=None):
    """Return papers as list of legacy dicts, optionally filtered by year."""
    sql = "SELECT * FROM papers WHERE 1=1"
    params = []
    if start_year is not None:
        sql += " AND year >= ?"
        params.append(start_year)
    if end_year is not None:
        sql += " AND year <= ?"
        params.append(end_year)
    sql += " ORDER BY id"

    cur = conn.cursor()
    rows = cur.execute(sql, params).fetchall()
    return [row_to_paper_dict(r) for r in rows]


def get_paper_count(conn):
    """Return total number of papers in the DB."""
    cur = conn.cursor()
    return cur.execute("SELECT COUNT(*) FROM papers").fetchone()[0]


def get_paper_count_by_db(conn, database):
    """Return number of papers from a specific database (WoS or Scopus)."""
    cur = conn.cursor()
    return cur.execute("SELECT COUNT(*) FROM papers WHERE dataBase = ?", (database,)).fetchone()[0]


# ---------------------------------------------------------------------------
# SQL-based duplicate removal
# ---------------------------------------------------------------------------

def remove_duplicates_sql(conn):
    """
    Remove duplicate papers using SQL window functions.
    Matches on titleNorm+firstAuthorNorm or DOI.
    Returns stats dict compatible with preProcessBrief.
    """
    cur = conn.cursor()

    stats = {
        'duplicatedPapersCount': 0,
        'removedPapersWoS': 0,
        'removedPapersScopus': 0,
        'duplicatedWithDifferentCitedBy': 0,
    }

    # Phase 1: Title + first author dedup
    # Find groups with duplicates based on titleNorm + firstAuthorNorm
    cur.execute("""
        SELECT titleNorm, firstAuthorNorm, GROUP_CONCAT(id) as ids,
               GROUP_CONCAT(citedBy) as cited_bys,
               GROUP_CONCAT(dataBase) as databases,
               GROUP_CONCAT(eid) as eids,
               COUNT(*) as cnt
        FROM papers
        WHERE titleNorm != ''
        GROUP BY titleNorm, firstAuthorNorm
        HAVING cnt > 1
    """)
    title_groups = cur.fetchall()

    ids_to_delete = set()
    update_cited = {}  # id -> new citedBy
    update_dupl = {}   # id -> list of dup eids

    for group in title_groups:
        ids = [int(x) for x in group['ids'].split(',')]
        cited_bys = [int(x) for x in group['cited_bys'].split(',')]
        databases = group['databases'].split(',')
        eids = group['eids'].split(',')

        # Sort: WoS first (alphabetically reversed), then by id
        combined = list(zip(ids, cited_bys, databases, eids))
        combined.sort(key=lambda x: (0 if x[2] == 'WoS' else 1, x[0]))

        keeper = combined[0]
        keeper_id = keeper[0]
        keeper_cited = keeper[1]

        dup_eids = []
        for item in combined[1:]:
            dup_id, dup_cited, dup_db, dup_eid = item
            ids_to_delete.add(dup_id)
            dup_eids.append(dup_eid)

            if dup_db == 'WoS':
                stats['removedPapersWoS'] += 1
            else:
                stats['removedPapersScopus'] += 1

            if dup_cited != keeper_cited:
                stats['duplicatedWithDifferentCitedBy'] += 1

            # Average cited by
            keeper_cited = int((keeper_cited + dup_cited) / 2)

            stats['duplicatedPapersCount'] += 1

        update_cited[keeper_id] = keeper_cited
        # Get existing duplicatedIn for keeper
        existing = cur.execute("SELECT duplicatedIn FROM papers WHERE id = ?", (keeper_id,)).fetchone()
        existing_eids = []
        if existing and existing['duplicatedIn']:
            existing_eids = existing['duplicatedIn'].split(';')
        update_dupl[keeper_id] = existing_eids + dup_eids

    # Phase 2: DOI-only dedup (for papers not already marked for deletion)
    cur.execute("""
        SELECT doi, GROUP_CONCAT(id) as ids,
               GROUP_CONCAT(citedBy) as cited_bys,
               GROUP_CONCAT(dataBase) as databases,
               GROUP_CONCAT(eid) as eids,
               COUNT(*) as cnt
        FROM papers
        WHERE doi != '' AND id NOT IN ({})
        GROUP BY doi
        HAVING cnt > 1
    """.format(','.join(str(x) for x in ids_to_delete) if ids_to_delete else '-1'))
    doi_groups = cur.fetchall()

    for group in doi_groups:
        ids = [int(x) for x in group['ids'].split(',')]
        cited_bys = [int(x) for x in group['cited_bys'].split(',')]
        databases = group['databases'].split(',')
        eids = group['eids'].split(',')

        combined = list(zip(ids, cited_bys, databases, eids))
        combined.sort(key=lambda x: (0 if x[2] == 'WoS' else 1, x[0]))

        keeper = combined[0]
        keeper_id = keeper[0]
        keeper_cited = keeper[1]

        dup_eids = []
        for item in combined[1:]:
            dup_id, dup_cited, dup_db, dup_eid = item
            if dup_id in ids_to_delete:
                continue
            ids_to_delete.add(dup_id)
            dup_eids.append(dup_eid)

            if dup_db == 'WoS':
                stats['removedPapersWoS'] += 1
            else:
                stats['removedPapersScopus'] += 1

            if dup_cited != keeper_cited:
                stats['duplicatedWithDifferentCitedBy'] += 1

            keeper_cited = int((keeper_cited + dup_cited) / 2)
            stats['duplicatedPapersCount'] += 1

        if dup_eids:
            update_cited[keeper_id] = keeper_cited
            existing = update_dupl.get(keeper_id, [])
            if not existing:
                row = cur.execute("SELECT duplicatedIn FROM papers WHERE id = ?", (keeper_id,)).fetchone()
                if row and row['duplicatedIn']:
                    existing = row['duplicatedIn'].split(';')
            update_dupl[keeper_id] = existing + dup_eids

    # Apply updates
    for kid, new_cited in update_cited.items():
        cur.execute("UPDATE papers SET citedBy = ? WHERE id = ?", (new_cited, kid))

    for kid, dup_eids in update_dupl.items():
        cur.execute("UPDATE papers SET duplicatedIn = ? WHERE id = ?",
                     (';'.join(dup_eids), kid))

    # Delete duplicates
    if ids_to_delete:
        # Delete in batches to avoid SQL variable limits
        id_list = list(ids_to_delete)
        batch_size = 500
        for i in range(0, len(id_list), batch_size):
            batch = id_list[i:i+batch_size]
            placeholders = ','.join(['?'] * len(batch))
            cur.execute("DELETE FROM keywords WHERE paper_id IN ({})".format(placeholders), batch)
            cur.execute("DELETE FROM papers WHERE id IN ({})".format(placeholders), batch)

    conn.commit()
    return stats


# ---------------------------------------------------------------------------
# Topic queries (Phase 3)
# ---------------------------------------------------------------------------

def topic_discovery_sql(conn, criterion, start_year, end_year, only_first=False,
                        filter_sub_topic="", limit=10, offset=0):
    """
    Discover top topics via SQL GROUP BY on keywords table.
    Returns list of (keyword, count) tuples.
    """
    cur = conn.cursor()

    if only_first:
        sql = """
            SELECT k.keyword, COUNT(*) as cnt
            FROM keywords k
            JOIN papers p ON k.paper_id = p.id
            WHERE k.field = ?
              AND k.position = 0
              AND p.year BETWEEN ? AND ?
        """
    else:
        sql = """
            SELECT k.keyword, COUNT(*) as cnt
            FROM keywords k
            JOIN papers p ON k.paper_id = p.id
            WHERE k.field = ?
              AND p.year BETWEEN ? AND ?
        """

    params = [criterion, start_year, end_year]

    if filter_sub_topic:
        sql += " AND k.keyword LIKE ?"
        params.append('%' + filter_sub_topic.upper() + '%')

    sql += " GROUP BY k.keyword ORDER BY cnt DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = cur.execute(sql, params).fetchall()
    return [(r['keyword'], r['cnt']) for r in rows]


def topic_paper_match_sql(conn, criterion, sub_topics, start_year, end_year,
                          only_first=False, use_wildcard=False):
    """
    Find papers matching any of the sub_topics for a given criterion.
    Returns list of (paper_dict, matched_keyword, year) tuples.
    """
    cur = conn.cursor()

    results = []

    if use_wildcard:
        # For wildcard queries, we need LIKE patterns
        for sub_topic in sub_topics:
            pattern = sub_topic.upper().replace('*', '%')
            if only_first:
                sql = """
                    SELECT DISTINCT p.*, k.keyword
                    FROM keywords k
                    JOIN papers p ON k.paper_id = p.id
                    WHERE k.field = ?
                      AND k.keyword LIKE ?
                      AND k.position = 0
                      AND p.year BETWEEN ? AND ?
                """
            else:
                sql = """
                    SELECT DISTINCT p.*, k.keyword
                    FROM keywords k
                    JOIN papers p ON k.paper_id = p.id
                    WHERE k.field = ?
                      AND k.keyword LIKE ?
                      AND p.year BETWEEN ? AND ?
                """
            rows = cur.execute(sql, [criterion, pattern, start_year, end_year]).fetchall()
            for r in rows:
                results.append((row_to_paper_dict(r), r['keyword'], r['year']))
    else:
        # Exact match
        if not sub_topics:
            return results
        placeholders = ','.join(['?'] * len(sub_topics))
        upper_topics = [s.upper() for s in sub_topics]

        if only_first:
            sql = """
                SELECT DISTINCT p.*, k.keyword
                FROM keywords k
                JOIN papers p ON k.paper_id = p.id
                WHERE k.field = ?
                  AND k.keyword IN ({})
                  AND k.position = 0
                  AND p.year BETWEEN ? AND ?
            """.format(placeholders)
        else:
            sql = """
                SELECT DISTINCT p.*, k.keyword
                FROM keywords k
                JOIN papers p ON k.paper_id = p.id
                WHERE k.field = ?
                  AND k.keyword IN ({})
                  AND p.year BETWEEN ? AND ?
            """.format(placeholders)

        params = [criterion] + upper_topics + [start_year, end_year]
        rows = cur.execute(sql, params).fetchall()
        for r in rows:
            results.append((row_to_paper_dict(r), r['keyword'], r['year']))

    return results


def topic_year_counts_sql(conn, criterion, sub_topics, start_year, end_year,
                          only_first=False, use_wildcard=False):
    """
    Get per-year paper counts and citation sums for a set of sub-topics.
    Returns dict: {year: {'paper_count': N, 'cited_sum': M}}
    """
    cur = conn.cursor()

    if use_wildcard:
        conditions = []
        params = [criterion]
        for st in sub_topics:
            pattern = st.upper().replace('*', '%')
            conditions.append("k.keyword LIKE ?")
            params.append(pattern)
        topic_condition = "(" + " OR ".join(conditions) + ")"
    else:
        upper_topics = [s.upper() for s in sub_topics]
        placeholders = ','.join(['?'] * len(upper_topics))
        topic_condition = "k.keyword IN ({})".format(placeholders)
        params = [criterion] + upper_topics

    position_filter = "AND k.position = 0" if only_first else ""

    sql = """
        SELECT p.year, COUNT(DISTINCT p.id) as paper_count, SUM(p.citedBy) as cited_sum
        FROM keywords k
        JOIN papers p ON k.paper_id = p.id
        WHERE k.field = ?
          AND {topic_cond}
          {pos_filter}
          AND p.year BETWEEN ? AND ?
        GROUP BY p.year
        ORDER BY p.year
    """.format(topic_cond=topic_condition, pos_filter=position_filter)

    params.extend([start_year, end_year])
    rows = cur.execute(sql, params).fetchall()

    result = {}
    for r in rows:
        result[r['year']] = {
            'paper_count': r['paper_count'],
            'cited_sum': r['cited_sum'] or 0,
        }
    return result


# ---------------------------------------------------------------------------
# CSV export (preserves backward compat)
# ---------------------------------------------------------------------------

def export_to_csv(conn, path, format_type=None):
    """Export all papers from DB to CSV in Scopus or WoS field format."""
    if format_type is None:
        format_type = globalVar.SAVE_RESULTS_ON

    papers = get_all_papers(conn)

    # Import paperSave to reuse its existing CSV writing logic
    import paperSave
    paperSave.saveResults(papers, path)


def clear_db(conn):
    """Delete all papers and keywords from the database."""
    cur = conn.cursor()
    cur.execute("DELETE FROM keywords")
    cur.execute("DELETE FROM papers")
    conn.commit()
