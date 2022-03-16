import os
import re
import xml.etree.ElementTree as ET
from datetime import date
import pandas as pd


class Read_xml():
    def __init__(self, directory) -> None:
        self.directory = directory

    def all_files(self):
        return [os.path.join(self.directory, arq) for arq in os.listdir(self.directory) if arq.lower().endswith('.xml')]

    def nfe_data(self, xml):
        root = ET.parse(xml).getroot()
        nsNfe = {"ns": "http://www.portalfiscal.inf.br/nfe"}

        # DADOS DA NFE

        nfe = self.check_none(root.find("./ns:NFe/ns:infNFe/ns:ide/ns:nNF", nsNfe))
        serie = self.check_none(root.find("./ns:NFe/ns:infNFe/ns:ide/ns:serie", nsNfe))
        data_emissao = self.check_none(root.find("./ns:NFe/ns:infNFe/ns:ide/ns:dhEmi", nsNfe))
        data_emissao = F'{data_emissao[:4]}{data_emissao[5:7]}{data_emissao[8:10]}'

        # DADOS EMITENTES

        chave = self.check_none(root.find("./ns:protNFe/ns:infProt/ns:ide/ns:chNFe", nsNfe))
        cnpj_emitente = self.check_none(root.find("./ns:NFe/ns:infNFe/ns:emit/ns:CNPF", nsNfe))
        nome_emitente = self.check_none(root.find("./ns:NFe/ns:infNFe/ns:emit/ns:xNome", nsNfe))

        cnpj_emitente = self.format_cnpj(cnpj_emitente)

        valorNfe = self.check_none(root.find("./ns:NFe/ns:infNFe/ns:total/ns:ICMSTot/ns:vNF", nsNfe))
        data_importacao = date.today().strftime('%Y%m%d')
        data_saida = ''
        usuario = ''

        itemNota = 1
        notas = []

        for item in root.findall("./ns:NFe/ns:infNFe/ns:det", nsNfe):
            # DADOS DOS ITENS

            cod = self.check_none(item.find(".ns:prod/ns:cProd", nsNfe))
            qntd = self.check_none(item.find(".ns:prod/ns:qCom", nsNfe))
            descricao = self.check_none(item.find(".ns:prod/ns:xProd", nsNfe))
            unidade_medida = self.check_none(item.find(".ns:prod/ns:uCom", nsNfe))
            valorProd = self.check_none(item.find(".ns:prod/ns:vProd", nsNfe))

            dados = [nfe, serie, data_emissao, chave, cnpj_emitente, nome_emitente, valorNfe, itemNota, cod, qntd,
                     descricao, unidade_medida, valorProd, data_importacao, usuario, data_saida]

            notas.append(dados)
            itemNota += 1

        return notas

    def check_none(self, var):
        if var == None:
            return ''
        else:
            try:
                return var.text.replace('.', ',')
            except:
                return var.text

    def format_cnpj(self, cnpj):
        try:
            cnpj = f'{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}'
            return cnpj
        except:
            return ''


if __name__ == "__main__":

    xml = Read_xml(".")
    all = xml.all_files()

    for i in all:
        result = xml.nfe_data(i)
        nome = str(i)
        nome = re.sub('.xml', '', nome)
        result = pd.DataFrame(result)
        result.to_csv(str(nome)+ '.csv', sep=';')
        result.to_json(str(nome) + '.json')

        print(result)
