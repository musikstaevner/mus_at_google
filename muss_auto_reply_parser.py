#!/usr/bin/env python
# -*- coding: latin-1 -*-


import logging, email
from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail

from datamodel import ElevInfo
from datamodel import TransportData

# equals an enum to govern the path in my statemachine
Header, Enavn, Eadr, Epostby, Ecpr, Eepost, Emobil, Einstrument, Eniveau, Eene, Erabat, Fnavn, Fadr, Fpostby, Fepost, Ffnum, Fmnum, Besked = range(18)

THeader, Tnavn, Tepost, ToOlle, OnStation, FromOlle, OffStation, Tbesked = range(8)

AHeader, Anavn, Aepost, Aftensmad, Aftenskaffe, Overnatning, Mokost, Abesked, Pris = range(9)

data = {}
tdata = {}
adata = {}

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

        Cfoot = u"""
-- 
MVH fr. robot

Du modtager dette brev fordi vi har modtaget en tilmelding på http://musikstaevner.dk, hvis dette skulle være en fejl må du meget gerne lade os det vide på tilmelding@musikstaevner.dk"""


        
        
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
                logging.error("besked parser failed somehow")


    def parse_transport(self, lines):

        state = THeader
        Terror = ""
        tdata.clear()

        for line in lines:
            logging.debug("line type = " + type(line).__name__)
            logging.debug( "line = " + line)
            logging.debug( "state = %u" %( state )   )

            
            #skip blanks
            if len(line) < 2 : continue

            # skip label lines
            if line.find("-:") >=  0: continue
            if line.find(u"Emne: Til") >=  0: continue

            #as long as we haven't  seen the first "navn:"
            # we are sill in the header and just skips ahead
            if state == THeader:
                if line.find("Navn:") < 0:
                    continue
                else:
                    state = Tnavn
                    continue

            #we are not in the header any more,
            # so check if we need to change state
            # first see if we are in the "Besked" part, then do not search keywords
            if state < Tbesked:
                if line.find("E-post:") >=  0: state = Tepost ; continue
                if line.find("Til") >=  0: state = ToOlle ; continue
                if line.find("r P") >=  0: state = OnStation ; continue
                if line.find("Fra") >=  0: state = FromOlle ; continue
                if line.find("r AF") >=  0: state = OffStation ; continue
                if line.find("Evt. besked") >=  0: state = Tbesked ; continue


            # When get here we have a data line, the state tels us where to store the data
            # note: 'besked' part is different, in that it has multiplie lines
            if state != Tbesked:
                rest = line[3:]
                logging.debug( "DEBUG:rest = %s" %(  rest)   )
                tdata[state] = rest.rstrip()
            elif state == Tbesked:
                if tdata.has_key(state):
                    tdata[state] += line
                else:
                    tdata[state] = line
            else:
                logging.error("besked parser failed somehow")

        #refine and validate result
        if tdata.has_key(ToOlle):
            if tdata[OnStation].find(u"Vælg") >= 0:
                tdata[OnStation] = (u"Ikke valgt")
        else:
            tdata[OnStation] = u""
            
        if tdata.has_key(FromOlle):
            if tdata[OffStation].find(u"Vælg") >= 0:
                tdata[OffStation] = (u"Ikke valgt")
        else:
            tdata[OffStation] = u""

        # some debug logging
        for LL in range(0,8):
            if tdata.has_key(LL):
                logging.debug("%s" % repr(tdata[LL]))


    def store_transport(self):
        trans_d = TransportData()

        trans_d.Navn = tdata[Tnavn]
        trans_d.Epost = tdata[Tepost]
        trans_d.From = tdata[OnStation]
        trans_d.To = tdata[OffStation]
        if tdata.has_key(Tbesked):
            trans_d.Besked = tdata[Tbesked][:500]
        else:
            trans_d.Besked = ""
            
        trans_d.put()

    def respond_transport(self):
        
        trans_info = u"modtaget en tilmelding til fællestranspoert\n"
        trans_info += u"fra %s - %s\n" % (tdata[Tnavn], tdata[Tepost])
        
        trans_txt = u"""
Hej %s

Tak for din tilmelding til Fællestransport
Vi har modtaget følgende tilmelding

""" % tdata[Tnavn]
        
        if  tdata.has_key(ToOlle):
            trans_txt +=u"Du deltager i fællestranport _til_ Ollerup\n"
            trans_info +=u"deltager i fællestranport _til_ Ollerup\n"
            if tdata[OnStation].find(u"Ikke valgt") >= 0:
                trans_txt += u"med har ikke valgt hvor du står på\n\n"
                trans_info += u"har dog ikke valgt hvor der stås på\n\n"
            else:
                trans_txt += u"og står på ved %s\n\n" % tdata[OnStation]
                trans_info += u"og står på ved %s\n" % tdata[OnStation]
        
        if  tdata.has_key(FromOlle):
            trans_txt +=u"Du deltager i fællestranport _fra_ Ollerup\n"
            trans_info +=u"deltager i fællestranport _fra_ Ollerup\n"
            if tdata[OffStation].find(u"Ikke valgt") >= 0:
                trans_txt += u"med har ikke valgt hvor du står på\n\n"
                trans_info += u"har dog ikke valgt hvor der stås på\n\n"
            else:
                trans_txt += u"og står af ved %s\n\n" % tdata[OffStation]
                trans_info += u"og står af ved %s\n\n" % tdata[OffStation]
        
            
        if tdata.has_key(Tbesked):
            Tbesked_txt = ( "\nNB. vi modtog også denne besked fra dig\n"
                            '"%s"\n' % tdata[Tbesked])
            Tbesked_info = ("\nder var også denne besked\n"
                            '"%s"\n' % tdata[Tbesked])
        else:
            Tbesked_txt = ""
            Tbesked_info = ""
        
        Tfoot_txt = u"""
Prisen kan variere efter antal og afstand men plejer at ligge i omegnen af 200 kr.

Når vi kommer lidt tættere på stævnestart får du besked om priser og togtider. 
Fællestransport betales ved ankomst til stævnet
%s
-- 
MVH fr. robot

Du modtager dette brev fordi vi har modtaget en tilmelding på http://musikstaevner.dk, hvis dette skulle være en fejl må du meget gerne lade os det vide på tilmelding@musikstaevner.dk
        """ % Tbesked_txt
        
        Tfoot_info = "%s-- \nMVH fr. robot\n" % Tbesked_info

        
        tmessage = mail.EmailMessage(sender="robot@musikstaevner.dk",
                                     to = "%s" % tdata[Tepost],
                                     reply_to = "bestyrelse@musikstaevner.dk",
                                     subject = u"tilmelding til fællestransport",
                                     body = trans_txt + Tfoot_txt
                                     )


        tmessage.send()

        tbmessage = mail.EmailMessage(sender="robot@musikstaevner.dk",
                                     to = "bestyrelse@musikstaevner.dk",
                                     reply_to = "bestyrelse@musikstaevner.dk",
                                     subject = u"tilmelding til fællestransport",
                                     body = trans_info + Tfoot_info
                                     )


        tbmessage.send()


    def parse_afslutning(self, lines):

        state = AHeader
        adata.clear()
        price_aftensmad=60
        price_aftenskaffe=25
        price_overnatning=100
        price_mokost=60
        
        
        for line in lines:
            logging.debug("line type = " + type(line).__name__)
            logging.debug( "line = " + line)
            logging.debug( "state = %u" %( state )   )

            
            #Things to skip
            if len(line) < 2 : continue #blanks
            if line.find("-:") >=  0: continue
            if line.find(u"Emne: Afs") >=  0: continue
            if line.find(u"Antal:") >=  0: continue

            #as long as we haven't  seen the first "navn:"
            # we are sill in the header and just skips ahead
            if state == AHeader:
                if line.find("Navn:") < 0:
                    continue
                else:
                    state = Anavn
                    continue

            #we are not in the header any more,
            # so check if we need to change state
            # first see if we are in the "Besked" part, then do not search keywords
            if state < Abesked:
                if line.find(u"E-post:") >=  0: state = Aepost ; continue
                if line.find(u"Aftensmad") >=  0: state = Aftensmad ; continue
                if line.find(u"Aftenskaffe") >=  0: state = Aftenskaffe ; continue
                if line.find(u"Overnatning") >=  0: state = Overnatning ; continue
                if line.find(u"Mokost") >=  0: state = Mokost ; continue
                if line.find(u"Evt. besked") >=  0: state = Abesked ; continue


            # When get here we have a data line, the state tels us where to store the data
            # note: 'besked' part is different, in that it has multiplie lines
            if state != Abesked:
                rest = line[3:]
                logging.debug( "DEBUG:rest = %s" %(  rest)   )
                adata[state] = rest.rstrip()
            elif state == Abesked:
                if adata.has_key(state):
                    adata[state] += line
                else:
                    adata[state] = line
            else:
                logging.error("besked parser failed somehow")

        # some debug logging
        for LL in range(0,9):
            if adata.has_key(LL):
                logging.debug("%s" % repr(adata[LL]))

        #refine result
        try: #convert strins to ints
            adata[Aftensmad]   = int(adata[Aftensmad])
            adata[Aftenskaffe] = int(adata[Aftenskaffe])
            adata[Overnatning] = int(adata[Overnatning])
            adata[Mokost]      = int(adata[Mokost])
        except (ValueError, TypeError):
            logging.error("a conversion went wrong")
         
        adata[Pris]=(adata[Aftensmad] * price_aftensmad +
                    adata[Aftenskaffe] * price_aftenskaffe +
                    adata[Overnatning] * price_overnatning +
                    adata[Mokost] * price_mokost
                    )
        
        # some debug logging
        for LL in range(0,9):
            if adata.has_key(LL):
                logging.debug("%s" % repr(adata[LL]))



    def store_afslutning(self):
        afslut_d = TransportData()

        afslut_d.Navn        =  adata[Anavn]
        afslut_d.Epost       =  adata[Aepost]
        afslut_d.Aftensmad   =  adata[Aftensmad]  
        afslut_d.Aftenskaffe =  adata[Aftenskaffe]
        afslut_d.Overnatning =  adata[Overnatning]
        afslut_d.Mokost      =  adata[Mokost]     
        afslut_d.Pris        =  adata[Pris]
        if tdata.has_key(Tbesked):
            afslut_d.Besked  =  adata[Abesked][:500]
        else:
            afslut_d.Besked  = ""
        
        afslut_d.put()

    def respond_afslutning(self):
     
        afslut_info = u"modtaget en tilmelding til afslutning\n"
        afslut_info += u"fra %s - %s\n" % (adata[Anavn], adata[Aepost])
        
        afslut_txt = u"""   
Hej %s

Tak for din tilmelding til afslutningen
Vi har modtaget følgende:

""" % adata[Anavn]
        afslut_data_txt = u""
        if adata[Aftensmad] > 0:
            afslut_data_txt +=u"%s til aftensmad\n" % adata[Aftensmad]
        if adata[Aftenskaffe] > 0:
            afslut_data_txt +=u"%s til aftenskaffe\n" % adata[Aftenskaffe]
        if adata[Overnatning] > 0:
            afslut_data_txt +=u"%s til Overnatning\n" % adata[Overnatning]
        if adata[Mokost] > 0:
            afslut_data_txt +=u"%s til Mokost\n" % adata[Mokost]
            
        if adata.has_key(Abesked):
            Abesked_txt = ( "\nNB. vi modtog også denne besked fra dig\n"
                            '"%s"\n' % adata[Abesked])
            Abesked_info = ("\nder var også denne besked\n"
                            '"%s"\n' % adata[Abesked])

        else:
            Abesked_txt = ""
            Abesked_info = ""

        Afoot_txt = u"""
Den samlede betaling udgør kr. %s som skal indbetales 
på konto nr. 3627 0002360039 inden 8 dage, sammen med restbeløbet for stævnet, som udgør kr. 2500.


Når vi kommer lidt tættere på stævnestart får du nærmere besked om diverse tidspunkter for forestilling, aftensmad o.s.v.
%s
-- 
MVH fr. robot

Du modtager dette brev fordi vi har modtaget en tilmelding på http://musikstaevner.dk, hvis dette skulle være en fejl må du meget gerne lade os det vide på tilmelding@musikstaevner.dk
        """ % (adata[Pris] , Bbesked_txt)
        
        Afoot_info = "prisen er beregnet til %s\n%s\n-- \nMVH fr. robot\n" % (adata[Pris], Abesked_info)

        
        amessage = mail.EmailMessage(
            sender="robot@musikstaevner.dk",
            to = "%s" % adata[Aepost],
            reply_to = "bestyrelse@musikstaevner.dk",
            subject = u"tilmelding til afslutning",
            body = afslut_txt + afslut_data_txt + Afoot_txt
            )
        amessage.send()

        abmessage = mail.EmailMessage(
            sender="robot@musikstaevner.dk",
            to = "bestyrelse@musikstaevner.dk",
            reply_to = "bestyrelse@musikstaevner.dk",
            subject = u"tilmelding til afslutning",
            body = afslut_info + afslut_data_txt + Afoot_info
            )
        abmessage.send()



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
                     + "to: " + mail_message.to
                     + "\n who wrote :/n"
                     + mail_message.body.decode())

        #we will parse the letter line for line
        lines = mail_message.body.decode().splitlines()

        logging.debug("lines type= " + type(lines).__name__)

        # some version of google dev server has an error
        # that deliveres str instead of uniciode. Fix that
        for line_itr in range(0, len(lines)):
            lines[line_itr] = self.to_unicode_or_bust(lines[line_itr])

        logging.debug("%s" % mail_message.to )
        if mail_message.to.find("tilmelding") >= 0:
            self.parse_tilmelding(lines)
            self.store_tilmelding()
            self.respond_tilmelding()
        elif mail_message.to.find("transport")>= 0:
            self.parse_transport(lines)
            self.store_transport()
            self.respond_transport()
        elif mail_message.to.find("afslutning")>= 0:
            self.parse_afslutning(lines)
            self.store_afslutning()
            self.respond_afslutning()
        else:
            send_mail_to_admins("robot@musikstaevner.dk",
                                "unhandled mail", 
                                "Received a message from: "
                                    + mail_message.sender
                                    + "to: " + mail_message.to
                                    + "\n who wrote :/n"
                                    + mail_message.body.decode())
        


application = webapp.WSGIApplication([FormHandler.mapping()], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
