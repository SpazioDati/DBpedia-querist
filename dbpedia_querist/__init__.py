"""
dbpedia-querist
A simple library to query dbpedia and airpedia endpoints
"""
import re
from sparql import Service,SparqlException

ENDPOINTS = {
'en':       'http://dbpedia.org/sparql',
'it':       'http://it.dbpedia.org/sparql',
'fr':       'http://fr.dbpedia.org/sparql',
'airpedia': 'http://www.airpedia.org/sparql'
}

class DBpediaQuerist(object):

    def __init__(self,lang='en',resultlimit=1000):
        assert isinstance(resultlimit,int)
        assert resultlimit >= 0
        assert lang in ENDPOINTS.keys()

        self.lang=lang
        self.resultlimit=resultlimit
        self.endpoint=ENDPOINTS[lang]
        self.Service = Service(self.endpoint)

    def query(self,qb):
        assert isinstance(qb,SPARQLQueryBuilder)

        # count total no. of results
        cq = SPARQLQueryBuilder(qb)
        orig_offset = qb.get_offset() or 0
        cq.select('COUNT(*)').orderby(None).offset(None)
        try:
            rescq = int([str(res[0]) for res in self.Service.query(cq.build()).fetchone()][0])
        except SparqlException as e:
            print 'ERROR: ', e.code
            print e.message
            return
        numres = rescq-orig_offset

        # get actual results
        results = list()
        reslim=self.resultlimit or numres or -1
        for off in range(orig_offset,numres,reslim):
            nqb = SPARQLQueryBuilder(qb).offset(off)
            print nqb.build()
            try:
                resnq = self.Service.query(nqb.build())
                results += resnq.fetchall()
            except SparqlException as e:
                print 'ERROR: ', e.code
                print e.message
                return
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
    print
    print 'Create DBpediaQuerist object'
    dbq=DBpediaQuerist('it')

    print 'Standard query'
    qb=SPARQLQueryBuilder()

    qb.select('?idn,?church').where('''
               ?church a <http://dbpedia.org/ontology/ReligiousBuilding>.
               ?church <http://dbpedia.org/ontology/wikiPageID> ?idn
              '''
             ).orderby('?idn')
    result = dbq.query(qb)
    print 'Test passed'
    
    print
    print 'Copy constructor and query with offset'
    qb2=SPARQLQueryBuilder(qb)
    qb2.offset(5158)
    result = dbq.query(qb2)
    print 'Test passed'

    print
    print 'Empty query (raises SPARQLQueryBuilder AssertionError)'
    qb3=SPARQLQueryBuilder()
    try:
        qb3.build()
    except AssertionError:
        print 'AssertionError raised'

    qb3.select('?something')
    try:
        qb3.build()
    except AssertionError:
        print 'AssertionError raised'
    print 'Test passed'

    print
    print 'Query with error (raise an error in SPARQL endpoint)'
    print 'result is None'
    qb4=SPARQLQueryBuilder()
    qb4.where('?something')
    qb4.where('someerror')
    result = dbq.query(qb4)
    assert result is None
    print 'Test passed'

