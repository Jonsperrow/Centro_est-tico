import PySimpleGUI as sg
from datetime import datetime
import pickle
import os

class SalaoEsteticaApp:
    def __init__(self):
        self.clientes = {}
        self.agendamentos = {}
        self.fluxo_caixa = []

        
        self.load_data()

        sg.theme('DarkAmber')

        layout = [
            [sg.Text('Cadastro de Clientes')],
            [sg.InputText(key='NOME', size=(30, 1)), sg.InputText(key='TELEFONE', size=(20, 1))],
            [sg.Button('Cadastrar Cliente')],
            [sg.Combo(values=self.ordenar_clientes(), key='CLIENTE_SELECIONADO_EXCLUIR', size=(30, 1)), sg.Button('Excluir Cliente')],
            [sg.Text('_' * 50)],
            [sg.Text('Agendamento de Horários')],
            [sg.Text('Data do Agendamento')],
            [sg.InputText('', key='DATA', size=(20, 1), disabled=True), sg.Button('Selecionar Data')],
            [sg.Text('Horário'), sg.Text('Cliente')],
            [sg.Combo(values=self.gerar_horarios(), key='HORARIO', size=(10, 1)), sg.Combo(values=self.ordenar_clientes(), key='CLIENTE', size=(30, 1))],
            [sg.Text('Serviço'), sg.Text('Valor')],
            [sg.Combo(values=['Massagem', 'Dread', 'Unha', 'Depilação', 'Limpeza de Pele'], key='SERVICO', size=(20, 1)), sg.InputText(key='VALOR', size=(10, 1))],
            [sg.Button('Agendar')],
            [sg.Text('_' * 50)],
            [sg.Text('Agendamentos')],
            [sg.Listbox(values=self.formatar_agendamentos(), key='AGENDAMENTOS', size=(50, 10))],
            [sg.Button('Excluir Agendamento')],
            [sg.Text('_' * 50)],
            [sg.Text('Fluxo de Caixa')],
            [sg.Listbox(values=self.fluxo_caixa, key='FLUXO_CAIXA', size=(50, 10))],
            [sg.Text('Valor Total: R$'), sg.Text('0.00', key='VALOR_TOTAL')],
        ]

        layout_with_scroll = [
            [sg.Column(layout, scrollable=True, vertical_scroll_only=True, size=(600, 400))]
        ]

        self.window = sg.Window('Salão de Estética Mariane Miranda', layout_with_scroll, finalize=True)
        self.update_valor_total()

    def gerar_horarios(self):
        horarios = []
        for hora in range(7, 12):
            horarios.append(f"{hora:02d}:00")
        for hora in range(14, 19):
            horarios.append(f"{hora:02d}:00")
        return horarios

    def ordenar_clientes(self):
        return sorted(self.clientes.values())

    def formatar_agendamentos(self):
        formatted = []
        for data, horarios in self.agendamentos.items():
            for horario, detalhes in horarios.items():
                formatted.append(f"{data} - {horario} - {detalhes['cliente']} - {detalhes['servico']} - R${detalhes['valor']:.2f}")
        return formatted

    def run(self):
        while True:
            event, values = self.window.read()

            if event == sg.WIN_CLOSED:
                self.save_data()
                break
            elif event == 'Selecionar Data':
                self.selecionar_data()
            elif event == 'Cadastrar Cliente':
                self.cadastrar_cliente(values)
            elif event == 'Excluir Cliente':
                self.excluir_cliente(values)
            elif event == 'Agendar':
                self.agendar_horario(values)
            elif event == 'Excluir Agendamento':
                self.excluir_agendamento(values)

        self.window.close()

    def selecionar_data(self):
        data = sg.popup_get_date(close_when_chosen=True, no_titlebar=False, title='Selecione a Data')
        if data:
            data_formatada = f"{data[1]:02d}/{data[0]:02d}/{data[2]}"
            self.window['DATA'].update(data_formatada)

    def cadastrar_cliente(self, values):
        nome = values['NOME']
        telefone = values['TELEFONE']
        if nome and telefone:
            self.clientes[telefone] = nome
            self.window['CLIENTE'].update(values=self.ordenar_clientes())
            self.window['CLIENTE_SELECIONADO_EXCLUIR'].update(values=self.ordenar_clientes())
            self.window['NOME'].update('')
            self.window['TELEFONE'].update('')

    def excluir_cliente(self, values):
        cliente_selecionado = values['CLIENTE_SELECIONADO_EXCLUIR']
        if cliente_selecionado:
            telefone = next((tel for tel, nome in self.clientes.items() if nome == cliente_selecionado), None)
            if telefone:
                del self.clientes[telefone]
                self.window['CLIENTE'].update(values=self.ordenar_clientes())
                self.window['CLIENTE_SELECIONADO_EXCLUIR'].update(values=self.ordenar_clientes())

    def agendar_horario(self, values):
        data = values['DATA']
        horario = values['HORARIO']
        cliente = values['CLIENTE']
        servico = values['SERVICO']
        valor = values['VALOR']
        if data and horario and cliente and servico and valor:
            valor = float(valor.replace(',', '.'))
            if data not in self.agendamentos:
                self.agendamentos[data] = {}
            self.agendamentos[data][horario] = {'cliente': cliente, 'servico': servico, 'valor': valor}
            self.fluxo_caixa.append(f"{data} - {horario} - {cliente} - {servico} - R${valor:.2f}")
            self.update_valor_total()
            self.window['AGENDAMENTOS'].update(values=self.formatar_agendamentos())
            self.window['FLUXO_CAIXA'].update(values=self.fluxo_caixa)
            self.window['HORARIO'].update('')
            self.window['CLIENTE'].update('')
            self.window['SERVICO'].update('')
            self.window['VALOR'].update('')

    def excluir_agendamento(self, values):
        selecionado = values['AGENDAMENTOS']
        if selecionado:
            agendamento_str = selecionado[0]
            data, horario, _, _, valor_str = agendamento_str.split(' - ')
            valor = float(valor_str.replace('R$', '').replace(',', '.'))
            del self.agendamentos[data][horario]
            if not self.agendamentos[data]:
                del self.agendamentos[data]
            self.fluxo_caixa.remove(agendamento_str)
            self.update_valor_total()
            self.window['AGENDAMENTOS'].update(values=self.formatar_agendamentos())
            self.window['FLUXO_CAIXA'].update(values=self.fluxo_caixa)

    def update_valor_total(self):
        total = sum(float(item.split(' - ')[4].replace('R$', '').replace(',', '.')) for item in self.fluxo_caixa)
        self.window['VALOR_TOTAL'].update(f'R${total:.2f}')

    def save_data(self):
        with open('dados_clientes.pkl', 'wb') as f:
            pickle.dump(self.clientes, f)
        with open('dados_agendamentos.pkl', 'wb') as f:
            pickle.dump(self.agendamentos, f)
        with open('fluxo_caixa.pkl', 'wb') as f:
            pickle.dump(self.fluxo_caixa, f)

    def load_data(self):
        if os.path.exists('dados_clientes.pkl'):
            with open('dados_clientes.pkl', 'rb') as f:
                self.clientes = pickle.load(f)
        if os.path.exists('dados_agendamentos.pkl'):
            with open('dados_agendamentos.pkl', 'rb') as f:
                self.agendamentos = pickle.load(f)
        if os.path.exists('fluxo_caixa.pkl'):
            with open('fluxo_caixa.pkl', 'rb') as f:
                self.fluxo_caixa = pickle.load(f)

if __name__ == "__main__":
    app = SalaoEsteticaApp()
    app.run()

