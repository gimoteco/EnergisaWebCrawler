import scrapy
import logging

logging.getLogger('scrapy').setLevel(logging.WARNING)

class Spider1(scrapy.Spider):
    name = 'Energisa'
    link_de_autenticacao = 'http://agenciaweb.energisa.com.br:8088/AgenciaWeb/autenticar/autenticar.do'
    def __init__(self, unidade_consumidora, cpf, **kwargs):
        super().__init__(**kwargs)
        self.unidade_consumidora = unidade_consumidora
        self.cpf = cpf

    def start_requests(self):
        yield scrapy.http.FormRequest(self.link_de_autenticacao, formdata={
            'numeroDocumentoCPF': self.cpf,
            'sqUnidadeConsumidora':	self.unidade_consumidora,
            'tipoUsuario': 'clienteUnCons',
            'tpDocumento': 'CPF',
        })

    def parse(self, resposta):
        seletor_do_contratante = ".textoGeral::text"
        url_do_historico = resposta.css('div#mn table tbody tr td.textoMenu.itemMenu a::attr(href)')[7].extract()
        print(resposta.css(seletor_do_contratante).extract_first())
        yield resposta.follow(url_do_historico, callback=self.processar_faturas)

    def processar_faturas(self, resposta):
        for link_da_fatura in resposta.css('table#histFat tbody tr td a')[0:1]:
            href_da_fatura = link_da_fatura.css('::attr(href)').extract_first().replace('imprimirSegundaVia.do', 'exibirFat.do')
            yield resposta.follow(href_da_fatura, callback=self.baixar_fatura)

    def baixar_fatura(self, resposta):
        with open('fatura.pdf', 'wb') as fatura:
            fatura.write(resposta.body)
            