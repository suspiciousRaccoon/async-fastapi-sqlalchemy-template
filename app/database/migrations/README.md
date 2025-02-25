## Alembic Commands CheatSheet


### Creating migrations

```bash
alembic revision -m "some descriptive message here"
```

A new file will be created inside `./versions`. Upgrading and downgrading logic must be defined manually.

### Running migrations

```bash
alembic upgrade "revision_id"
```

The "revision_id" will be in the specific `./versions/revision_id` file.

```bash
alembic upgrade ae1
```

It is possible to use a partial number instead of the full id.

```bash
alembic upgrade head
```

Alternatively, we can simply use `head` to use the latest revision.

```bash
alembic upgrade +2
```

Or specify a number of migrations to apply.

### Get current migrations

```bash
alembic current
```

```bash
alembic history
```

### Downgrading migrations

```bash
alembic downgrade "revision_id"
```

We can use the same arguments as `running migrations`.

```bash
alembic downgrade base
```

Or `base` to downgrade to the start.

### More documentation

https://alembic.sqlalchemy.org/en/latest/tutorial.html

### Autogenrating migrations

```bash
alembic revision -m "some descriptive message here" --autogenerate
```

Although it has some limitations...
https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect
