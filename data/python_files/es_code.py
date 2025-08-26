# Python code generated for language: es
# Original prompt: Genere el código Python para lo siguiente: una función copia varios bytes de una ubicación de memoria a otra. El primer argumento es el destino; El segundo argumento es la fuente y el tercer argumento es el número de bytes para copiar. El búfer tiene 256 bytes de largo, por lo que hay mucho espacio para copiar el mensaje.

def memcpy(dest, src, n):
    dest[:n] = src[:n]