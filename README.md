DBpedia-querist
=========================

A simple library to query DBpedia and Airpedia endpoints



Examples
--------


To query a given DBpedia, create a DBpediaQuerist object and a 
SPARQLQueryBuilder object. SPARQLQueryBuilder allows to create simple SELECT 
queries.

The following example queries Italian DBpedia multiple times to obtain all 
the results. So in this case the queries listed below are generated.

```python
from dbpedia_querist import DBpediaQuerist,SPARQLQueryBuilder

dbq = DBpediaQuerist('it')
qb = SPARQLQueryBuilder()
qb.select('?idn,?church')
qb.where('''?church a <http://dbpedia.org/ontology/ReligiousBuilding>.
            ?church <http://dbpedia.org/ontology/wikiPageID> ?idn
         '''
        )
qb.orderby('?idn')
result = dbq.query(qb)
```

```
SELECT ?idn,?church WHERE {
                    ?church a <http://dbpedia.org/ontology/ReligiousBuilding>.
                    ?church <http://dbpedia.org/ontology/wikiPageID> ?idn
                    }
                    order by ?idn

SELECT ?idn,?church WHERE {
                    ?church a <http://dbpedia.org/ontology/ReligiousBuilding>.
                    ?church <http://dbpedia.org/ontology/wikiPageID> ?idn
                    }
                    order by ?idn
                    offset 1000
[...]
SELECT ?idn,?church WHERE {
                    ?church a <http://dbpedia.org/ontology/ReligiousBuilding>.
                    ?church <http://dbpedia.org/ontology/wikiPageID> ?idn
                    }
                    order by ?idn
                    offset 7000
```