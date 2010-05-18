from google.appengine.ext import db



class ElevInfo(db.Model):
      ElevNavn = db.StringProperty()
      ElevAdresse = db.StringProperty()
      ElevPostBy = db.StringProperty()
      ElevCpr  = db.StringProperty()
      ElevEpost = db.StringProperty()
      ElevMobil = db.StringProperty()
      ElevInstrument = db.StringProperty()
      ElevNiveau = db.StringProperty()
      ElevEnerum = db.StringProperty()
      ElevSRabat = db.StringProperty()
      ForaeldreNavn = db.StringProperty()
      ForaeldreAdresse = db.StringProperty()
      ForaeldrePostBy = db.StringProperty()
      ForaeldreEpost = db.StringProperty()
      ForaeldreFastnet = db.StringProperty()
      ForaeldrMobil = db.StringProperty()
      Besked = db.StringProperty(multiline=True)
      TilmeldtDate = db.DateTimeProperty(auto_now_add=True)


class TransportData(db.Model):
      Navn = db.StringProperty()
      Epost = db.StringProperty()
      From = db.StringProperty()
      To = db.StringProperty()
      Besked = db.StringProperty(multiline=True)
      TilmeldtDate = db.DateTimeProperty(auto_now_add=True)

class AfslutData(db.Model):
      Navn = db.StringProperty()
      Epost = db.StringProperty()
      Aftensmad = db.IntegerProperty()
      Aftenskaffe = db.IntegerProperty()
      Overnatning = db.IntegerProperty()
      Mokost = db.IntegerProperty()
      Pris = db.IntegerProperty()
      Besked = db.StringProperty(multiline=True)
      TilmeldtDate = db.DateTimeProperty(auto_now_add=True)
