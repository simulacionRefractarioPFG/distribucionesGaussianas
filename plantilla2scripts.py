import sys
import os	

'''
	Crea los casos a simular a partir de una plantilla.
	Con distintas proporciones de oxidos, diferentes valores medios y desviaciones tipicas.
	Entre estos se aproxima una distribucion normal con 'n_sizes' tamanos discretos. 
	Los scripts input que comparten la misma proporcion se guardan en un mismo directorio.
'''

#############
# Variables #
#############

# Valores de radio mu minimo y maximo considerados
mu_min = 100		# micras
mu_max = 1500		# micras
# Desviaciones tipicas minimas y maximas
sigma_min = 10
sigma_max = 500
# Steps
prop_step  = 5       # Paso porcentual en la proporcion de MgO en la mezcla
mu_step    = 300	 # Micras
sigma_step = 50		 # Micras
# Numero de diferentes radios para aproximar la distribucion gausiana con valores discretos
n_radios = 10.0				    # Importante tomar este valor como un float
n_sizes  = n_radios + 1 
radioMinimoConsiderado = 100	# Micras

##########################################
# Experimentos con distribucion gausiana #
##########################################

# Crea o vacia el contenido de scripts para dejar lugar a los nuevos experimentos
os.system("sudo mkdir ./scripts")
os.system("sudo rm -r ./scripts/*")

# Variacion de las proporciones en la mezcla, de 50 a 100% de MgO
for percen_MgO in range(50,100+prop_step,prop_step):
	# Directorios para ordenar por proporciones
	os.system("sudo mkdir ./scripts/input_MgO-%.1f" % (percen_MgO))
	# Variacion del radio minimo de particula
	for mu in range(mu_min, mu_max+mu_step, mu_step):
		# Variacion del radio maximo de particula
		for sigma in range(sigma_min, sigma_max+sigma_step, sigma_step):


			# Creacion de intervalos y archivo con intervalos. n_sizes entre (mu-3sigma) y (mu+3sigma).
			interFile = open('intervalos.txt','w')
			interFile.write("%.3f\n %.3f\n" % (mu, sigma)) # Las dos primeras lineas detallan mu y sigma
			radio = []
			for i in range(0,int(n_sizes)):
				radio.append((mu - 3*sigma)+(6*sigma/(n_sizes-1))*i)
				if(radio[i] >= radioMinimoConsiderado):
					interFile.write("%.3f\n" % radio[i])

			interFile.close()

			# Se toma el radio medio entre dos puntos
			R = []
			for i in range(0,len(radio)-1):
				if(radio[i] >= radioMinimoConsiderado):
					R.append((radio[i]+radio[i+1])/2)

			R_min = R[0]
			R_max = R[-1]
			os.system("octave GaussPercen.m")

			# Lee resultados con las propociones en masa de cada intervalo
			resultados = open('proporciones.txt','r')
			proporciones = []

			for line in resultados.readlines():
				proporciones.append(line)

			resultados.close()
			proporciones = list(map(float, proporciones))

			# Carpetas para albergar la geometria y resultados de la simulacion
			os.system("sudo mkdir ./scripts/input_MgO-%.1f/mu%.0f_sigma%.0f" % (percen_MgO, mu, sigma))
			os.system("sudo cp -R ./meshes ./scripts/input_MgO-%.1f/mu%.0f_sigma%.0f/" % (percen_MgO, mu, sigma))
			os.system("sudo mkdir ./scripts/input_MgO-%.1f/mu%.0f_sigma%.0f/post" % (percen_MgO, mu, sigma))
			os.system("sudo chmod -R 777 ./scripts/")

			# Comando linux 'sed'(String EDitor)
			# Sustitucion de valores en in.plantilla1, in.plantilla2, in.plantilla3 para el nuevo script
			os.system("sed -e 's/VAR_n_sizes/%d/g' -e 's/VAR_percen_MgO/%.1f/g' -e 's/VAR_mu/%.0f/g' \
			  -e 's/VAR_sigma/%.0f/g' -e 's/VAR_R_min/%.0f/g' -e 's/VAR_R_max/%.0f/g' \
			  in.plantilla1 > scripts/%s/in1.MgO_%.1f_mu%.0f_sigma%.0f" % (len(R)	, percen_MgO, mu, sigma,
																		   R_min, R_max, 'input_MgO-%.1f/mu%.0f_sigma%.0f' % (percen_MgO, mu, sigma), percen_MgO, mu, sigma))
			os.system("sed -e 's/VAR_R_min/%.0f/g' -e 's/VAR_R_max/%.0f/g' in.plantilla2 > \
			  scripts/%s/in2.MgO_%.1f_mu%.0f_sigma%.0f" % (R_min, R_max, 'input_MgO-%.1f/mu%.0f_sigma%.0f' % 
														   (percen_MgO, mu, sigma), percen_MgO, mu, sigma))
			os.system("sed -e 's/VAR_R_min/%.0f/g' -e 's/VAR_R_max/%.0f/g' in.plantilla3 > \
			  scripts/%s/in3.MgO_%.1f_mu%.0f_sigma%.0f" % (R_min, R_max, 'input_MgO-%.1f/mu%.0f_sigma%.0f' % 
														   (percen_MgO, mu, sigma), percen_MgO, mu, sigma))
			os.system("sed -e 's/VAR_R_min/%.0f/g' in.plantilla4 > scripts/%s/in4.MgO_%.1f_mu%.0f_sigma%.0f" % 
					  (R_min, 'input_MgO-%.1f/mu%.0f_sigma%.0f' % (percen_MgO, mu, sigma), percen_MgO, mu, sigma))

			#############################################################################
			# Lineas para el input script con los radios y las plantillas de particulas #
			#############################################################################
			radiusString = ""
			templatesString = ""
			particledistibution = ("fix pdd2 all particledistribution/discrete 5430 ${n_templates} ")
			for i in range(0,len(R)):
				# Introduce los distintos radios
				radiusString = radiusString + "\n" + ("variable r%d equal %.3f" % (i, R[i]))
				# Introduce las diferentes plantillas de las particulas
				templatesString = templatesString + "\n" + ("fix pts%d all particletemplate/sphere "
															"1 atom_type 1 density constant ${rho_MgO} radius constant ${r%d}") % (2*i, i)
				templatesString = templatesString + "\n" + ("fix pts%d all particletemplate/sphere "
															"1 atom_type 2 density constant ${rho_Al2O3} radius constant ${r%d}") % (2*i+1, i)
				particledistibution = particledistibution + "pts%d %.5f pts%d %.5f " \
															% (2*i, proporciones[i]*percen_MgO/100, 2*i+1, proporciones[i]*(100-percen_MgO)/100)


			filename = "scripts/%s/in1.MgO_%.1f_mu%.0f_sigma%.0f" % ('input_MgO-%.1f/mu%.0f_sigma%.0f' \
																	 % (percen_MgO, mu, sigma), percen_MgO, mu, sigma)
			tempfileName = "scripts/%s/tempfile" % ('input_MgO-%.1f/mu%.0f_sigma%.0f' % (percen_MgO, mu, sigma))
			file = open(filename,'r')
			tempfile = open(tempfileName,'a')
			# Lee cada linea y escribe en el archivo temporal
			for line in file.readlines():
				if line.startswith('-----'):
					tempfile.write(radiusString)

				elif line.startswith('~~~~~'):
					tempfile.write(templatesString)	

				elif line.startswith('*****'):
					tempfile.write(particledistibution)	

				else:
					tempfile.write(line)

			file.close
			tempfile.close

			# Sobreescribe el archivo input 1 con el contenido del archivo temporal recien creado
			os.system("sudo mv scripts/%s/tempfile scripts/%s/in1.MgO_%.1f_mu%.0f_sigma%.0f" \
					  % ('input_MgO-%.1f/mu%.0f_sigma%.0f' % (percen_MgO, mu, sigma), \
						 'input_MgO-%.1f/mu%.0f_sigma%.0f' % (percen_MgO, mu, sigma), percen_MgO, mu, sigma))

			# Genera archivos para la ejecucion de la simulacion completa
			#os.system("sudo cp ./ejecuta ./scripts/input_MgO-%.1f/mu%.0f_sigma%.0f/" % (percen_MgO, mu, sigma))
			os.system("sed -e 's/proporcion/%.1f/g' -e 's/MU/%.0f/g' -e 's/SIGMA/%.0f/g' \
			  ./ejecuta.py > scripts/%s/ejecuta.py" % (percen_MgO, mu, sigma,
													   'input_MgO-%.1f/mu%.0f_sigma%.0f' % (percen_MgO, mu, sigma)))



# Borra archivos temporales proporciones.txt e intervalos.txt
os.system("sudo rm proporciones.txt intervalos.txt")