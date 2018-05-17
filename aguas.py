import scrapy
import logging
try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract
import re

logging.getLogger('scrapy').setLevel(logging.WARNING)

class AguasGuarirobaSpider(scrapy.Spider):
    name = 'AguasGuariroba'
    start_urls = ['http://age.gssbr.com.br/guariroba/views/login.jsf']
    
    def __init__(self, numero_da_ligacao, cpf, **kwargs):
        super().__init__(**kwargs)
        self.ligacao, self.digito_verificador_da_ligacao = numero_da_ligacao.split('-')
        self.cpf = cpf

    def parse(self, resposta):
        link_do_captcha = resposta.css("img[id='formLogin:captchaImg2']::attr(src)").extract_first()
        yield resposta.follow(link_do_captcha, callback=self.download_do_captcha)
        self.link_do_post = resposta.css("#formLogin::attr(action)").extract_first()
        self.view_state = resposta.css("input[id='javax.faces.ViewState']::attr(value)").extract_first()


    def download_do_captcha(self, resposta):
        with open('captcha.jpg', 'wb') as imagem_do_captcha:
            imagem_do_captcha.write(resposta.body)
            
        resposta_do_captcha = re.sub("[^0-9]", "", pytesseract.image_to_string(Image.open('./captcha.jpg')))

        print('CAPTCHA: ', resposta_do_captcha)
        dados = {
            'formLogin': 'formLogin',
            'tipoDocLoginRadio': 'FISICA',
            'formLogin:cpfCpnjInput': self.cpf,
            'formLogin:numLigaInput': self.ligacao,
            'formLogin:digVInput': self.digito_verificador_da_ligacao,
            'formLogin:captchaInput': resposta_do_captcha,
            'formLogin:j_idt46': 'formLogin:j_idt46',
            'javax.faces.partial.ajax': 'true',
            'javax.faces.partial.execute': 'formLogin',
            'javax.faces.partial.render': 'formLogin:captchaImg2 formLogin:msgInvalid2 formLogin:outputPanelCaptcha2',
            'javax.faces.source': 'formLogin:j_idt46',
            'javax.faces.ViewState': self.view_state
        }
        
        yield scrapy.http.FormRequest(resposta.urljoin(self.link_do_post), formdata=dados, callback=self.logado)

    def logado(self, resposta):
        print(resposta)
        print(resposta.css("table tbody[id='j_idt190:j_idt191_data'] tr td span::text").extract())

                