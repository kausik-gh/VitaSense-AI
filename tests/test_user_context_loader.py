import pytest

from db.user_context_loader import (
    DAILY_TABLES,
    USER_CONTEXT_TABLES,
    load_recent_daily_data,
    load_user_health_context,
)


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, table_name, response_data, calls, error=False):
        self.table_name = table_name
        self.response_data = response_data
        self.calls = calls
        self.error = error

    def select(self, columns):
        self.calls.append((self.table_name, "select", columns))
        return self

    def eq(self, column, value):
        self.calls.append((self.table_name, "eq", column, value))
        return self

    def maybe_single(self):
        self.calls.append((self.table_name, "maybe_single"))
        return self

    def gte(self, column, value):
        self.calls.append((self.table_name, "gte", column, value))
        return self

    def order(self, column, desc=False):
        self.calls.append((self.table_name, "order", column, desc))
        return self

    def limit(self, value):
        self.calls.append((self.table_name, "limit", value))
        return self

    def execute(self):
        self.calls.append((self.table_name, "execute"))
        if self.error:
            raise RuntimeError("query failed")
        return FakeResponse(self.response_data)


class FakeSupabase:
    def __init__(self, responses=None, errors=None):
        self.responses = responses or {}
        self.errors = set(errors or [])
        self.calls = []

    def table(self, table_name):
        self.calls.append((table_name, "table"))
        return FakeQuery(
            table_name,
            self.responses.get(table_name),
            self.calls,
            error=table_name in self.errors,
        )


def _assert_user_id_first_filter(calls, table_name, expected_user_id):
    table_calls = [call for call in calls if call[0] == table_name]
    filter_calls = [call for call in table_calls if call[1] in {"eq", "gte", "order", "limit"}]

    assert filter_calls[0] == (table_name, "eq", "user_id", expected_user_id)


@pytest.mark.asyncio
async def test_user_context_loader_filters_every_table_by_user_id_first():
    supabase = FakeSupabase(
        responses={table_name: {"user_id": 42, "value": table_name} for table_name in USER_CONTEXT_TABLES}
    )

    result = await load_user_health_context(supabase, 42)

    assert result["user_id"] == 42
    for table_name in USER_CONTEXT_TABLES:
        assert result[table_name]["user_id"] == 42
        _assert_user_id_first_filter(supabase.calls, table_name, 42)


@pytest.mark.asyncio
async def test_daily_loader_filters_every_table_by_user_id_first_and_limits_days():
    supabase = FakeSupabase(
        responses={query.table_name: [{"user_id": 7, "value": query.table_name}] for query in DAILY_TABLES}
    )

    result = await load_recent_daily_data(supabase, 7, days=3)

    for query in DAILY_TABLES:
        assert result[query.table_name] == [{"user_id": 7, "value": query.table_name}]
        _assert_user_id_first_filter(supabase.calls, query.table_name, 7)
        assert (query.table_name, "limit", 3) in supabase.calls


@pytest.mark.asyncio
async def test_loaders_gracefully_handle_empty_rows_and_query_errors():
    context_supabase = FakeSupabase(errors={USER_CONTEXT_TABLES[0]})
    daily_supabase = FakeSupabase(errors={DAILY_TABLES[0].table_name})

    context = await load_user_health_context(context_supabase, 11)
    daily = await load_recent_daily_data(daily_supabase, 11)

    assert context[USER_CONTEXT_TABLES[0]] == {}
    assert daily[DAILY_TABLES[0].table_name] == []


@pytest.mark.asyncio
async def test_missing_single_profile_row_is_graceful():
    supabase = FakeSupabase(errors={USER_CONTEXT_TABLES[0]})

    class MissingRowQuery(FakeQuery):
        def execute(self):
            self.calls.append((self.table_name, "execute"))
            raise RuntimeError("406 Not Acceptable: JSON object requested, multiple (or no) rows returned")

    class MissingRowSupabase(FakeSupabase):
        def table(self, table_name):
            self.calls.append((table_name, "table"))
            return MissingRowQuery(table_name, None, self.calls, error=False)

    context = await load_user_health_context(MissingRowSupabase(), 11)

    assert context[USER_CONTEXT_TABLES[0]] == {}


@pytest.mark.asyncio
async def test_loaders_reject_invalid_user_id():
    with pytest.raises(ValueError, match="user_id"):
        await load_user_health_context(FakeSupabase(), 0)

    with pytest.raises(ValueError, match="user_id"):
        await load_recent_daily_data(FakeSupabase(), -1)
