%==============================================================
% Devuelve las proporciones en masa de cada intervalo de radios
% en una distribucion normal de media mu y desviacion sigma.
%============================================================== 

% Importa los datos generados del script de python
A = importdata('./intervalos.txt');

% Lee la informacion del archivo
mu = A(1);
sigma = A(2);
Intervalos = A(3:end);

% Calcula las probabilidades de cada intervalo
F = normcdf(Intervalos, mu, sigma);
for i = 1:(length(F)-1)
	prob(i) = F(i+1) - F(i);
end

% Desprecia valores menores al 0.1%
for i = 1:length(prob)
	if(prob(i)<0.0001)
		prob(i) = 0;
	end
end

% Vector en forma columna
prob = prob';

% Guarda los resultados generados
dlmwrite('./proporciones.txt',prob);

