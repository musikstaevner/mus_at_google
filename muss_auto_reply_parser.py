#!/usr/bin/env python
# -*- coding: latin-1 -*-


import logging, email
from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail

from datamodel import ElevInfo

# equals an enum to govern the path in my statemachine
Header, Enavn, Eadr, Epostby, Ecpr, Eepost, Emobil, Einstrument, Eniveau, Eene, Erabat, Fnavn, Fadr, Fpostby, Fepost, Ffnum, Fmnum, Besked = range(18)

data = {}

class FormHandler(InboundMailHandler):
    
    
    def store_tilmelding(self):
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
        elev.Besked = data[Besked][:500]

        elev.put()

    def respond_tilmelding(self):
        elev_txt = u"""
Elev:


%s
%s
%s

E-post: %s
Mobil: %s
Cpr: %s
Spiller %s på %s niveau
ønsker enkeltværelse: %s
Søskenderabat: %s
        """ % (data[Enavn], data[Eadr], data[Epostby], data[Eepost], data[Emobil], data[Ecpr],
               data[Einstrument], data[Eniveau], data[Eene], data[Erabat] )

        far_txt = u"""
Forældre/Værge


%s
%s
%s

E-post: %s
Fastnet: %s
Mobil: %s

        """ % (data[Fnavn], data[Fadr], data[Fpostby], data[Fepost], data[Ffnum], data[Fmnum])

        if data.has_key(Besked):
            besked_txt =u"Besked:\n%s" % data[Besked]
        else:
            besked_txt =u"Ingen besked"
        
        oplysninger = u"""
Herunder er de oplysninger vi har modtaget:

%s
%s
%s

        """ % (elev_txt, far_txt, besked_txt)
                

        Egreet=u"""
Hej %s

Vi glæder os til at se dig til Karmaugen 2010 :o))

Du kan følge med i de seneste nyheder om stævnet på http://musikstaevner.dk .

        """ % data[Enavn]


        Fgreet=u"""
hej %s


%s er nu tilmeldt Danske Musikstævner 2010.

For at tilmeldingen er bindende, skal du indbetale et depositum på kr. 500,- på konto nr. 3627 0002360039 inden 8 dage. Hvis du IKKE har hørt fra os 10 dage efter din tilmelding, er det fordi vi HAR modtaget din betaling..

Restbeløbet skal indbetales på samme kontonummer, Senest 8 uger før stævnestart.

Se danskemusikstaevner.dk. vedr. retningslinjer for tilbagebetaling af depositum og restbeløb ved afmelding.

I begyndelsen af april 2010 vil du modtage detaljeret information om stævnet. Indtil da kan du holde dig ajour på http://musikstaevner.dk.


        """ % (data[Fnavn] , data[Enavn])

        Cfoot = u"Du modtager dette brev fordi vi har modtaget en tilmelding på http://musikstaevner.dk, hvis dette skulle være en fejl må du meget gerne lade os det vide på tilmelding@musikstaevner.dk"
        
        
        # first send to bestyrelsen
        bmessage = mail.EmailMessage(sender="robot@musikstaevner.dk",
                                     subject = u"[Tilmelding] %s" % data[Enavn])
#       bmessage.to = "bestyrelse@musikstaevner.dk"
        bmessage.to = "mah@alslug.dk"
        bmessage.body = u"""
Jubii endnu en tilmelding :-D

%s

--
MVH fr. robot

        """ % oplysninger

        bmessage.send()

        # then send to elev
        emessage = mail.EmailMessage(sender="robot@musikstaevner.dk",
                                     to = "%s" % data[Eepost],
                                     reply_to = "bestyrelse@musikstaevner.dk",
                                     subject = u"tak for din tilmelding",
                                     body = Egreet + oplysninger + Cfoot
                                     )
        emessage.send()

        # last send to parrents/proxy pareents
        fmessage = mail.EmailMessage(sender="robot@musikstaevner.dk",
                                     to = "%s" % data[Fepost],
                                     reply_to = "bestyrelse@musikstaevner.dk",
                                     subject = u"tilmelding til Danske musikstævner 2010",
                                     body = Fgreet + oplysninger + Cfoot
                                     )
        fmessage.send()



    def to_unicode_or_bust(self, obj, encoding='utf-8'):
        if isinstance(obj, basestring):
            if not isinstance(obj, unicode):
                obj = unicode(obj, encoding)
                logging.info("fixed missing unicode")
        return obj


    def parse_tilmelding(self, lines):

        state = Header
        data.clear()

        for line in lines:
            logging.debug("line= " + type(line).__name__)

            logging.debug( "DEBUG:" + line)

            
            #skip blanks
            if len(line) < 2 : continue

            # skip label lines
            if line.find("-:") >=  0: continue
            if line.find("- Info om") >=  0: continue
            if line.find("Emne: Til") >=  0: continue

            #as long as we haven't  seen the first "navn:"
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
            logging.debug( "state = %u" %( state )   )
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
                logging.debug("Fpart")
                if line.find("navn:") >=  0: state = Fnavn ; continue
                if line.find("Adresse:") >=  0: state = Fadr ; continue
                if line.find("by:") >=  0: state = Fpostby ; continue
                if line.find("mail:") >=  0: state = Fepost ; continue
                if line.find("net nummer:") >=  0: state = Ffnum ; continue
                if line.find("Mobil nummer:") >=  0: state = Fmnum ; continue
                if line.find("Besked:") >=  0: state = Besked ; continue

            # When get here we have a data line, the state telss us where to store the data
            # note: 'besked' part is different, in that it has multiplie lines
            if state != Besked:
                rest = line[3:]
                logging.debug( "DEBUG:rest = %s" %(  rest)   )
                data[state] = rest.rstrip()
            elif state == Besked:
                if data.has_key(state):
                    data[state] += line
                else:
                    data[state] = line
            else:
                print "problem, should newer get here"
            

    def receive(self, mail_message):
        
#        logging.basicConfig(level=logging.DEBUG)
#        self.request.charset='utf-8'
        

        logging.debug("mail_message type= " + type(mail_message).__name__)
        logging.debug("EncodedPayload encoding= " + str(mail_message.body.encoding))
        logging.debug("body type= " + type(mail_message.body).__name__)

        ## curcomvent bug in google api, not sure it is a safe way
        if mail_message.body.encoding == '8bit':
            mail_message.body.encoding = '7bit' 
            logging.info('Body encoding fixed')

        logging.info("Received a message from: "
                     + mail_message.sender
                     + " who wrote "
                     + mail_message.body.decode())

        
        #we will parse the letter line for line
        lines = mail_message.body.decode().splitlines()

        logging.debug("lines type= " + type(lines).__name__)

        # some version of google dev serber has an error
        # that deliveres str instead of uniciode. Fix that
        for line_itr in range(0, len(lines)):
            lines[line_itr] = self.to_unicode_or_bust(lines[line_itr])

        if mail_message.to.find("tilmelding") >= 0:
            self.parse_tilmelding(lines)
            self.store_tilmelding()
            self.respond_tilmelding()
        if mail_message.to.find("transport")>= 0:
            self.parse_transport(lines)
        if mail_message.to.find("afslutning")>= 0:
            self.parse_afslutning(lines)

        


application = webapp.WSGIApplication([FormHandler.mapping()], debug=False)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
