

import logging, email
from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from datamodel import ElevInfo

# equals an enum to govern the path in my statemachine
Header, Enavn, Eadr, Epostby, Ecpr, Eepost, Emobil, Einstrument, Eniveau, Eene, Erabat, Fnavn, Fadr, Fpostby, Fepost, Ffnum, Fmnum, Besked = range(18)

data = {}

class FormHandler(InboundMailHandler):
    
    
    def store(self):
        self.request.charset='utf-8'
        elev = ElevInfo()

        elev.ElevNavn = data[Enavn]
        elev.ElevAdresse = data[Eadr]
        elev.ElevPostBy = data[Epostby]
        elev.ElevCpr = data[Ecpr]
        elev.ElevEpost = data[Eepost]
        elev.ElevMobil = data[Emobil]
        elev.ElevInstrument = data[Einstrument]
        elev.ElevNiveau = data[Eniveau]
        elev.ElevEnerum = data[Eene]
        elev.ElevSRabat = data[Erabat]
        elev.ForaeldreNavn = data[Fnavn]
        elev.ForaeldreAdresse = data[Fadr]
        elev.ForaeldrePostBy = data[Fpostby]
        elev.ForaeldreEpost = data[Fepost]
        elev.ForaeldreFastnet = data[Ffnum]
        elev.ForaeldrMobil = data[Fmnum]
        elev.Besked = data[Besked]

        elev.put()

    def fix_encoding(self, message):
    
        if hasattr(message, 'body'):
            if isinstance(message.body, EncodedPayload):
                _log.debug(message.body.encoding)
                if message.body.encoding == '8bit':
                    message.body.encoding = '7bit' 
                    _log.debug('Body encoding fixed')
                    
        if hasattr(message, 'html'):    
            if isinstance(message.html, EncodedPayload):
                _log.debug(message.html.encoding)    
                if message.html.encoding == '8bit':
                    message.html.encoding = '7bit' 
                    _log.debug('HTML encoding fixed')
        if hasattr(message, 'attachments'):
            for file_name, data in _attachment_sequence(message.attachments):
                if isinstance(data, EncodedPayload):
                    _log.debug(data.encoding)
                    if data.encoding == '8bit':
                        data.encoding = '7bit'
                        _log.debug('Attachment encoding fixed')
        return message




    def receive(self, mail_message):
        
        logging.basicConfig(level=logging.DEBUG)
        self.request.charset='utf-8'
        
        state = Header

        #mail_message = self.fix_encoding(mail_message)
        logging.info("mail_message= " + type(mail_message).__name__)
        logging.info("EncodedPayload encoding= " + str(mail_message.body.encoding))
        if mail_message.body.encoding == '8bit':
            mail_message.body.encoding = '7bit' 
            logging.debug('Body encoding fixed')

        logging.info("Received a message from: "
                     + mail_message.sender
                     + " who wrote "
                     + mail_message.body.decode())

        #fetch the letter
        logging.info("body= " + type(mail_message.body).__name__)

        logging.info("body_decoded= "
                     + type(mail_message.body.decode()).__name__)
        
        lines = mail_message.body.decode().splitlines()

        logging.info("lines= " + type(lines).__name__)

        for utf8line in lines:
            logging.info("utf8line= " + type(utf8line).__name__)

            #line = unicode(utf8line, 'utf-8')
            line = utf8line
            logging.info( "DEBUG:" + line)

            
            #skip blanks
            if len(line) < 2 : continue

            # skip label lines
            if line.find("-:") >=  0: continue
            if line.find("- Info om") >=  0: continue
            if line.find("Emne: Til") >=  0: continue

            #as long as we havent  seen the first "navn:"
            # we are sill in the header and just skips ahead
            if state == Header:
                if line.find("navn:") < 0:
                    continue
                else:
                    state = Enavn
                    continue

            #we are not in the header any more,
            # so check if we need to change state
            # first see if we are in the E part
            logging.info( "DEBUG: state = %u" %( state )   )
            if state < 10 :
                if line.find("Adresse:") >=  0: state = Eadr ; continue
                if line.find("by:") >=  0: state = Epostby ; continue
                if line.find("nr.:") >=  0: state = Ecpr ; continue
                if line.find("mail:") >=  0: state = Eepost ; continue
                if line.find("Mobil nummer:") >=  0: state = Emobil ; continue
                if line.find("Jeg spiller p") >=  0: state = Einstrument ; continue
                if line.find("Niveau:") >=  0: state = Eniveau ; continue
                if line.find("relse:") >=  0: state = Eene ; continue
                if line.find("rabat:") >=  0: state = Erabat ; continue
            else: # we are in the F part
                logging.info("Fpart")
                if line.find("navn:") >=  0: state = Fnavn ; continue
                if line.find("Adresse:") >=  0: state = Fadr ; continue
                if line.find("by:") >=  0: state = Fpostby ; continue
                if line.find("mail:") >=  0: state = Fepost ; continue
                if line.find("net nummer:") >=  0: state = Ffnum ; continue
                if line.find("Mobil nummer:") >=  0: state = Fmnum ; continue
                if line.find("Besked:") >=  0: state = Besked ; continue



            #    print DEBUG state 
            # besked part is different in that it has multipli lines
            if state != Besked:
                rest = line[3:]
                logging.info( "DEBUG:rest = %s" %(  rest)   )
                logging.info( "DEBUG:rest = %s" %(  repr(rest))   )
                data[state] = rest.rstrip()
                logging.info( "DEBUG:%u %s" %( state , repr(data[state]))   )
            elif state == Besked:
                if data.has_key(state):
                    data[state] += line
                else:
                    data[state] = line
            else:
                print "problem, should newer get here"
            
        self.store()
                        






application = webapp.WSGIApplication([FormHandler.mapping()], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
