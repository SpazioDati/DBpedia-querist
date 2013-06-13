"""
dbpedia-querist
A simple library to query dbpedia and airpedia endpoints
"""
import re
from sparql import Service

ENDPOINTS = {
'en':       'http://dbpedia.org/sparql',
'it':       'http://it.dbpedia.org/sparql',
'fr':       'http://fr.dbpedia.org/sparql',
'airpedia': 'http://airpedia.org/sparql'
}

RESULTSLIMIT = 1000

class DBpediaQuerist(object):

    def __init__(self,lang='en'):
        self.lang=lang
        self.endpoint=ENDPOINTS[lang]
        self.Service = Service(self.endpoint)

    def query(self,qb):
        assert isinstance(qb,SPARQLQueryBuilder)

        # count total no. of results
        cq = SPARQLQueryBuilder(qb)
        orig_offset = qb.get_offset() or 0
        cq.select('COUNT(*)').orderby(None).offset(None)
        rescq = int([str(res[0]) for res in self.Service.query(cq.build()).fetchone()][0])
        numres = rescq-orig_offset

        # get actual results
        results = list()
        for off in range(orig_offset,numres,RESULTSLIMIT):
            nqb = SPARQLQueryBuilder(qb).offset(off)
            print nqb.build()
            resnq = self.Service.query(nqb.build())
            results += self.Service.query(nqb.build()).fetchall()

        return results

class SPARQLQueryBuilder(object):
    """
    A SPARQL query builder class
    """

    def __init__(self,qb=None):
       self._select=None
       self._where=None
       self._order=None
       self._offset=None
       self.query="""SELECT {select} WHERE {{
                      {where}
                     }}
                  """
       if isinstance(qb,SPARQLQueryBuilder):
           self._select=qb.get_select()
           self._where=qb.get_where()
           self._order=qb.get_orderby()
           self._offset=qb.get_offset()

    def select(self,select):
        self._select=select
        return self

    def where(self,where):
        self._where=where
        return self

    def orderby(self,order):
        self._order=order
        return self

    def offset(self,offset):
        if offset is not None:
            assert isinstance(offset,int)
        self._offset=offset
        return self

    def get_select(self):
        return self._select

    def get_where(self):
        return self._where

    def get_orderby(self):
        return self._order

    def get_offset(self):
        return self._offset

    def __str__(self):
        return self.build()

    def build(self):
        assert self._select
        assert self._where
        querytext=self.query.format(select=self._select,
                                    where=self._where
                                   )

        if self._order:
            querytext+="""order by {order}
                   """.format(order=self._order)

        if self._offset:
            querytext+="""offset {offset}
                   """.format(offset=str(self._offset))

        return querytext

if __name__ == "__main__":
    dbq = DBpediaQuerist('it')
    qb = SPARQLQueryBuilder()
    qb.select('?idn,?church')
    qb.where('''?church a <http://dbpedia.org/ontology/ReligiousBuilding>.
                ?church <http://dbpedia.org/ontology/wikiPageID> ?idn
             '''
            )
    qb.orderby('?idn')
    result = dbq.query(qb)

    qb2 = SPARQLQueryBuilder(qb)
    qb2.offset(158)
    result = dbq.query(qb2)
    print len(result)