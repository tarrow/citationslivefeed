import socketIO_client
import requests
import mwcites.utilities.extract
from mwcites.extractors import arxiv, doi, isbn, pubmed


class WikiNamespace(socketIO_client.BaseNamespace):
    def on_change(self, change):
        """
        ids = set(mwcites.utilities.extract.extract_ids(text, [doi, pubmed, isbn, arxiv]))
        for id in ids:
            print('\t'.split(id.type, id.id))
        """
        if change['type'] == 'edit' and change['namespace'] == 0:
            #print(change)
            newrevid=change['revision']['new']
            oldrevid=change['revision']['old']
            revids= str(newrevid) + '|' + str(oldrevid)
            payload = {'action':'query','prop':'revisions','rvprop':'content','revids':revids,'format':'json','formatversion':'2'}
            header = {'user-agent': 'Tarrow-Test client tarrow@ebi.ac.uk'}
            r=requests.get("https://en.wikipedia.org/w/api.php?", params=payload, headers=header)
            jsonresponse=r.json()
            #print(change)
            oldtext=jsonresponse['query']['pages'][0]['revisions'][0]['content']
            if not len(jsonresponse['query']['pages'][0]['revisions']) == 2:
                return
            newtext=jsonresponse['query']['pages'][0]['revisions'][1]['content']
            oldids = set(mwcites.utilities.extract.extract_ids(oldtext, [doi, pubmed, isbn, arxiv]))
            newids = set(mwcites.utilities.extract.extract_ids(newtext, [doi, pubmed, isbn, arxiv]))
            for id in oldids:
                if id not in newids:
                    print(id.type + ' ' + id.id + " removed")
            for id in newids:
                if id not in oldids:
                    print(id.type + ' ' + id.id + " added")




    def on_connect(self):
        self.emit('subscribe', 'en.wikipedia.org')


socketIO = socketIO_client.SocketIO('stream.wikimedia.org', 80)
socketIO.define(WikiNamespace, '/rc')


socketIO.wait(seconds=None)
