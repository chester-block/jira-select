Query Format
============

Jira-select queries are written in a YAML format,
but using section names inspired by SQL.

Here's a simple example that will return all Jira issues assigned to you:

.. code-block:: yaml

   select:
   - key
   - summary
   from: issues
   where:
   - assignee = "your-email@your-company.net"

Here's a query that uses _all_ of the possible sections,
but know that in real life, you're very unlikely to use them all at once:

.. code-block:: yaml

   select:
   - assignee
   - len(key)
   from: issues
   expand:
   - changelog
   where:
   - project = "MYPROJECT"
   order_by:
   - created
   group_by:
   - assignee
   having:
   - len(key) > 5
   sort_by:
   - len(key) desc
   limit: 100

Below, we'll go over what each of these sections are for in detail.

Overview
--------

.. csv-table:: Jira-select Query Sections
   :file: evaluation_location.csv
   :header-rows: 1

Ubiquitous
----------

``select``
~~~~~~~~~~

This section defines what data you would like to include in your report.
It should be a list of fields you would like to include in your document,
and *can* use custom functions (see :ref:`Query Functions` for options).

By default, the column will be named to match your field definition,
but you can overide that by providing a name using the format ``EXPRESSION as "NAME"``::

    somefunction(my_field) as "My Field Name"

``from``
~~~~~~~~

This section defines what you would like to query.
The value should be a string, and at the moment there is only one option: "issues".

``where``
~~~~~~~~~

This section is where you enter the JQL for your query.
This should be provided as a list of strings;
these strings will be ``AND``-ed together to generate the query sent to Jira.

You *cannot* use custom functions in this section
given that it is evaluated on your Jira server instead of locally.

``order_by``
~~~~~~~~~~~~

This section is where you enter your JQL ordeirng instructions and should
be a list of strings.

You *cannot* use custom functions in this section
given that it is evaluated on your Jira server instead of locally.

Common
------

``group_by``
~~~~~~~~~~~~

This section is where you can define how you would like your rows to be grouped.
This behaves similarly to SQL's ``GROUP BY`` statement in that rows sharing
the same result in your ``group_by`` expression will be grouped togehter.

For example; to count the number of issues by type that are assigned to you
you could run the following query:

.. code-block:: yaml

   select:
   - issuetype
   - len(key)
   from: issues
   where:
   - assignee = "your-email@your-company.net"
   group_by:
   - issuetype

.. Note::

   When executing an SQL query that uses a ``GROUP BY`` statement,
   you will always see just a single value for each column
   even if that column represents multiple rows' values.

   Unlike standard SQL,
   in Jira-select column values will always contain arrays of values
   when your column definition does not use a value entered in your ``group_by`` section.
   If you are surprised about a particular field showing an array holding values that are all the same,
   try adding that column to your ``group_by`` statement, too.

If you would like to perform an aggregation across all returned values,
you can provide ``True`` in your ``group_by`` statement.
This works because, for every row, ``True`` will evaluate to the same result
causing all rows to be grouped together:

.. code-block:: yaml

   select:
   - len(key)
   from: issues
   where:
   - assignee = "your-email@your-company.net"
   group_by:
   - True

You **can** use custom functions in this section.

``having``
~~~~~~~~~~

This section is where you can provide filtering instructions that Jql cannot handle
because they either require local functions or operate on grouped data.

You **can** use custom functions in this section.

``sort_by``
~~~~~~~~~~~

This section is where you can provide sorting instructions that Jql cannot handle
because they either require local functions or operate on grouped data.

You **can** use custom functions in this section.

``limit``
~~~~~~~~~

This sets a limit on how many rows will be returned.

Unusual
-------

``expand``
~~~~~~~~~~

Jira has a concept of "field expansion",
and although by default Jira-select will fetch "all" data,
that won't actually return quite all of the data.
You can find more information about what data this will return
by reading `the Jira documentation covering
"Search for issues using JQL (GET)" <https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get>`_.