from zeep import Client
from zeep.transports import Transport

class TCKimlikNoSorgula:
    def __init__(self, tc_kimlik_no, ad, soyad, dogum_yili):
        self.tc_kimlik_no = tc_kimlik_no
        self.ad = ad
        self.soyad = soyad
        self.dogum_yili = dogum_yili

    def sorgula(self):
        # WSDL URL'sini belirle
        wsdl_url = 'https://tckimlik.nvi.gov.tr/Service/KPSPublic.asmx?wsdl'

        # SOAP istemcisini oluştur
        transport = Transport(timeout=10)
        client = Client(wsdl=wsdl_url, transport=transport)

        # SOAP isteği için parametreleri belirle
        parameters = {
            'TCKimlikNo': self.tc_kimlik_no,
            'Ad': self.ad,
            'Soyad': self.soyad,
            'DogumYili': self.dogum_yili
        }

        # SOAP isteğini gönder ve yanıtı al
        response = client.service.TCKimlikNoDogrula(**parameters)

        return response

# Kullanım örneği
if __name__ == "__main__":
    tc_kimlik_no = '19451167026'
    ad = 'Ufukd'
    soyad = 'Çiçek'
    dogum_yili = 1995

    sorgu = TCKimlikNoSorgula(tc_kimlik_no, ad, soyad, dogum_yili)
    sonuc = sorgu.sorgula()

    if sonuc:
        print("T.C. Kimlik numarası doğrulandı.")
    else:
        print("T.C. Kimlik numarası doğrulanmadı.")





