import re

class Ponto:
	def __init__(self, NSR, dia, hora, pis):
		#Pattern para PIS
		patternPIS = re.compile(r'(\d{3})(\d{5})(\d{2})(\d{1})')
		replacePIS = r'\1.\2.\3-\4'               
		pis = re.sub(patternPIS, replacePIS, pis)

		self.NSR = NSR
		self.dia = dia
		self.hora = hora
		self.pis = pis


	def get_diaI(self):
		self.dia = self.dia[4:9] + "-" + self.dia[2:4] + "-" + self.dia[0:2]
		return self.dia

	def getNSR(self):
		return self.NSR

	def salvarDados(self):

		return 'salva'

	def excluirDados(self):
		return 'exclui'

	def editarDados(self):
		return 'edita'

	def retornaLista(self):
		return 'lista'
