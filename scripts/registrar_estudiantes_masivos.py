#!/usr/bin/env python3
"""
Script para registrar estudiantes masivos desde un archivo CSV
"""
import os
import csv
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.contrib.auth.models import User
from apps.core.models import PerfilUsuario

def registrar_estudiantes_desde_csv(archivo_csv):
    """Registra estudiantes desde un archivo CSV"""
    
    try:
        with open(archivo_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                username = row.get('username')
                email = row.get('email')
                password = row.get('password', 'EduNomad2024')
                first_name = row.get('first_name', '')
                last_name = row.get('last_name', '')
                
                if not username or not email:
                    print(f"❌ Datos incompletos: {row}")
                    continue
                
                # Verificar si ya existe
                if User.objects.filter(username=username).exists():
                    print(f"⚠️ Usuario {username} ya existe")
                    continue
                
                try:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name
                    )
                    
                    PerfilUsuario.objects.create(
                        usuario=user,
                        rol='ESTUDIANTE',
                        identificacion=f"EST-{user.id:06d}",
                        fecha_registro=datetime.now(),
                    )
                    
                    print(f"✅ Estudiante registrado: {username} ({first_name} {last_name})")
                    
                except Exception as e:
                    print(f"❌ Error con {username}: {e}")
                    
    except FileNotFoundError:
        print(f"❌ Archivo {archivo_csv} no encontrado")
    except Exception as e:
        print(f"❌ Error: {e}")

def crear_template_csv():
    """Crea un template CSV para registrar estudiantes"""
    template = """username,email,password,first_name,last_name
estudiante_006,estudiante006@edunomad.com,EduNomad2024,Andrés,Gómez
estudiante_007,estudiante007@edunomad.com,EduNomad2024,Patricia,Díaz
estudiante_008,estudiante008@edunomad.com,EduNomad2024,José,Ramírez
estudiante_009,estudiante009@edunomad.com,EduNomad2024,Marta,Flores
estudiante_010,estudiante010@edunomad.com,EduNomad2024,Luis,Torres
"""
    
    with open('estudiantes_template.csv', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print("✅ Template CSV creado: estudiantes_template.csv")

if __name__ == "__main__":
    print("📚 REGISTRO MASIVO DE ESTUDIANTES")
    print("=" * 50)
    
    # Crear template
    crear_template_csv()
    
    # Ejemplo de uso
    print("\n📝 Para registrar estudiantes desde CSV:")
    print("  python registrar_estudiantes_masivos.py")
    print("  Edita el archivo 'estudiantes_template.csv' con los datos")
    print("  Descomenta la línea: # registrar_estudiantes_desde_csv('estudiantes_template.csv')")
    
    # registrar_estudiantes_desde_csv('estudiantes_template.csv')
