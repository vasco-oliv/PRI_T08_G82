# PRI_T08_G82

## How to run

To run the project backend, you need to have installed docker app. Then you can open it and run the commands in the makefile:

```bash
`make up` - start Docker daemon and Solr.
`make down` - stop Docker daemon and Solr.
`make schema_boosted` - create the schema in Solr.
`make populate` - populate the Solr with the data.
```

## How to query the backend

Query formats are available in the config folder as the query_sysX.json files. To run a query, you can use the following command:

```bash
`make query QUERY=?` - run the query for the system chosen with default value 1.
```

If you want to have the results in a file with the TREC format, you can use the following command:

```bash
`make query_trec QUERY=?` - run the query for the system chosen with default value 1 and save the results in a file.
```

## How to run the frontend
