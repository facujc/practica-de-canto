# practica-de-canto
Aplicación para aprender a cantar bien.
El propósito de este proyecto es diseñar una herramienta que facilite el desarrollo de habilidades de canto específicas, como la entonación, el ritmo, la amplitud, etc. Para ello me valgo del diseño de distintos ejercicios que perfeccionan dichas areas (además de uno diseñado para calentar la voz), cada uno de ellos consiste primeramente en escuchar una secuencia de sonidos de tono/amplitud/duración/ritmo uniforme y variable (generados por la aplicación), secundariamente de reproducir dicha secuencia lo mejor posible (mientras se es grabado por la aplicación) y finalmente verificar visualmente (en el gráfico generado en base a la grabación de la voz obtenida) que los resultados obtenidos cumplan los requerimientos del usuario. La aplicación está desarrollada en lenguaje Python, posee una interfaz gráfica simple diseñada con TKInter (para la ventana) y Matplotlib (para la generación del gráfico de referencia), un metrónomo (que funciona en un thread separado) y las lecciones diseñadas por mí; la generación de sonido se realiza con la librería Pyo, la grabación de la voz con la librería PyAudio, y el reconocimiento de tono se realiza utilizando la librería praat-parselmouth.

Notas: Actualmente está en desarrollo, para una vista previa de la metodología de las lecciones ir a Inicio --> Entonacion --> Nota+Silencio --> Amplitud
