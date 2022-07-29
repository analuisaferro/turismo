from multiprocessing import context
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from requests import request
from contas.functions import validationsViagem

from contas.views import sair
from contas.models import Estado, Cidade
from senhas.models import Tipo_Veiculo, Viagem, Viagem_Turismo
from turismo.settings import BASE_DIR
from .models import Pontos_Turisticos
from .forms import ViagemForm
from .functions import get_random_string
import time
import pickle
from datetime import date, timedelta, datetime
import pdfkit
from turismo.decorators import membro_secretaria_required, membro_fiscais_required

@login_required
def inicio(request):
    return render(request, 'senhas/index.html')


@login_required
def cad_transporte(request):    
    hoje=date.today()
    viagens = Viagem.objects.filter(user=request.user, dt_Saida__range=[hoje, hoje+timedelta(days=365)], ativo=True)
    return render(request, 'senhas/cad_transporte.html', { 'viagens': viagens })

@login_required
def cadastrar_viagem_caledonia(request):    
    validation={'veiculo': {'state': True},
                'quant_passageiros': {'state': True}, 
                'cnpj_empresa_transporte': {'state': True}, 
                'cadastur_empresa_transporte': {'state': True}, 
                'cadastur_guia':  {'state': True}, 
                'telefone':  {'state': True}, 
                'celular':{'state': True}, 
                'chegada_saida':{'state_chegada': True, 'state_saida': True, 'msg': ''},
                'cidade': {'state': True},
                 'estado': {'state': True}, 
                 'empresa_transporte': {'state': True},
                'nome_guia':{'state': True}, 
                'responsavel_viagem':{'state': True}, 
                'contato_responsavel':{'state': True}            
                } 
    estados = Estado.objects.all().order_by('nome')
    if request.method == 'POST':                   
        form = ViagemForm(request.POST)
        # print(request.POST)
        #Aqui a VALIDATION toma novos valores de acordo com o FORM
        validation, valido=validationsViagem(request.POST, 'turismo')                                       
        if valido:                          
            viagens_caledonia_do_dia=Viagem.objects.filter(senha__contains='PC',ativo=True, dt_Chegada=request.POST['dt_chegada']).count()            
            if str(viagens_caledonia_do_dia)>=str(2):
                format = '%Y-%m-%d'
                dt=request.POST['dt_chegada']
                data=datetime.strptime(dt, format)
                messages.error(request, 'Vagas esgotadas para visitação no dia '+str(data.strftime('%d/%m/%Y'))) 
            else:
                try:
                    if request.POST['ficarao_hospedados']:
                        fh=True
                except:
                    fh=False      
                try:
                    if request.POST['restaurante_reservado']:
                        rr=True
                except:
                    rr=False       
                try:                
                    viagem=Viagem(        
                        responsavel_viagem=request.POST['responsavel_viagem'],
                        contato_responsavel=validation['contato_responsavel']['celular'],            
                        user=request.user, 
                        dt_Chegada=request.POST['dt_chegada'],
                        dt_Saida=request.POST['dt_chegada'],
                        ficarao_hospedados=fh,
                        hotel=request.POST['hotel'],
                        restaurante_reservado=rr,
                        restaurante=request.POST['restaurante'],
                        tipo_veiculo=Tipo_Veiculo.objects.get(id=request.POST['tipo_veiculo']),
                        quant_passageiros=request.POST['quant_passageiros'],
                        empresa_transporte=request.POST['empresa_transporte'],
                        cnpj_empresa_transporte=validation['cnpj_empresa_transporte']['cnpj'],
                        cadastur_empresa_transporte=validation['cadastur_empresa_transporte']['cadastur'],                    
                        obs=request.POST['obs'],
                        estado_origem=Estado.objects.get(id=request.POST['estado']),
                        cidade_origem=Cidade.objects.get(id=request.POST['cidade']),
                        ativo=True)
                    viagem.save()    
                            
                    
                    viagem.senha='PC'+get_random_string()+str(viagem.id)+get_random_string() 
                    viagem.save()
                    viagem_turismo=Viagem_Turismo(
                        viagem=viagem,
                        outros='Pico da Caledônia',
                        nome_guia=request.POST['nome_guia'],
                        cadastur_guia=validation['cadastur_guia']['cadastur'],
                        celular=validation['celular']['celular'],
                        telefone=validation['telefone']['telefone'],  
                        ativo=True                      
                    ) 
                    viagem_turismo.save() 
                    messages.success(request, 'Viagem cadastrada.')
                    return redirect('senhas:cad_transporte')               
                except Exception as E:
                    print(E)
        else:
            for i in validation:
                print('ERROR', i)
        veiculos=Tipo_Veiculo.objects.all()
        pontosTuristicos= Pontos_Turisticos.objects.filter(ativo=True)
    #Incluindo as informações coletas no contexto para uso no Template
        if 'turismo'=='turismo':
            viagem_turismo={
                'nome_guia': request.POST['nome_guia'], 
                'cadastur_guia': request.POST['cadastur_guia'],
                'celular': request.POST['celular'],
                'telefone': request.POST['telefone'],
            }
        try:
            estado=Estado.objects.get(id=request.POST['estado'])      
        except:
            estado=''
        try:
            cidade=Cidade.objects.get(id=request.POST['cidade'])
        except:
            cidade=''
        try: 
            if request.POST['ficarao_hospedados']:
                ficarao_hospedados=True
        except:
            ficarao_hospedados=False
        try: 
            if request.POST['restaurante_reservado']:
                restaurante_reservado=True
        except:
            restaurante_reservado=False
        try:
            tipo_veiculo=Tipo_Veiculo.objects.get(id=request.POST['tipo_veiculo'])            
        except:
            tipo_veiculo=''
        pontos_selecionados=[]        
        try:
            for u in request.POST.getlist('pontos_turisticos'):
                pontos_selecionados.append(Pontos_Turisticos.objects.get(nome=u))
        except:
            pass
        context={ 
            'form': form, 
            'validation': validation, 
            'veiculos': veiculos, 
            'pontos': pontosTuristicos,
            'tipo': 'turismo',
            'titulo': 'CADASTRAR',
            'estado_': estado,
            'estados': estados,  
            'cidade': cidade,
            'viagem': {'responsavel_viagem': request.POST['responsavel_viagem'],
                        'contato_responsavel': request.POST['contato_responsavel'],
                        'dt_Chegada2': request.POST['dt_chegada'],
                       'dt_Saida2': request.POST['dt_chegada'],
                    #    'estado_origem': request.POST['estado'],
                    #    'cidade_origem': request.POST['cidade'],
                       'empresa_transporte': request.POST['empresa_transporte'],
                       'cnpj_empresa_transporte': request.POST['cnpj_empresa_transporte'],
                       'cadastur_empresa_transporte': request.POST['cadastur_empresa_transporte'],
                       'quant_passageiros': request.POST['quant_passageiros'],
                       'tipo_veiculo': tipo_veiculo,
                       'obs': request.POST['obs'],
                       'ficarao_hospedados': ficarao_hospedados,
                       'restaurante_reservado': restaurante_reservado,
                       'restaurante': request.POST['restaurante'],
                       'hotel': request.POST['hotel']
                    },                                  
            'viagem_turismo': viagem_turismo,
            'pontos_selecionados': pontos_selecionados
        }
        return render(request, 'senhas/cadastros/caledonia.html', context)
    form=ViagemForm()
    veiculos=Tipo_Veiculo.objects.all()
    context={
        'form': form,
        'validation': validation,
        'titulo': 'CADASTRAR',
        'estados': estados,
        'veiculos': veiculos
    }
    return render(request, 'senhas/cadastros/caledonia.html', context)

def get_validar_caledonia(request):
    fail=False
    alert=''
    viagens_caledonia_do_dia=Viagem.objects.filter(senha__contains='PC',ativo=True, dt_Chegada=request.GET.get('date')).count()            
    if str(viagens_caledonia_do_dia)>=str(2):
        format = '%Y-%m-%d'
        dt=request.GET.get('date')
        data=datetime.strptime(dt, format)
        fail=True
        alert='Vagas esgotadas para visitação no dia '+str(data.strftime('%d/%m/%Y')+'. Escolha outra data.')
    return JsonResponse({
        'fail': fail,
        'alert': alert

    })
@login_required
def viagem_inclui(request, tipo):
    # Essa variavel VALIDATION é iniciada aqui para não haver conflito 
    # enquanto não existir uma requisição POST
    validation={'veiculo': {'state': True},
                'quant_passageiros': {'state': True}, 
                'cnpj_empresa_transporte': {'state': True}, 
                'cadastur_empresa_transporte': {'state': True}, 
                'cadastur_guia':  {'state': True}, 
                'telefone':  {'state': True}, 
                'celular':{'state': True}, 
                'chegada_saida':{'state_chegada': True, 'state_saida': True, 'msg': ''},
                'cidade': {'state': True},
                 'estado': {'state': True}, 
                 'empresa_transporte': {'state': True},
                'nome_guia':{'state': True}, 
                'responsavel_viagem':{'state': True}, 
                'contato_responsavel':{'state': True}} 
    
    estados = Estado.objects.all().order_by('nome')
    if request.method == 'POST':                   
        form = ViagemForm(request.POST)
        # print(request.POST)
        #Aqui a VALIDATION toma novos valores de acordo com o FORM
        validation, valido=validationsViagem(request.POST, tipo)                                       
        if valido:     
            try:
                if request.POST['ficarao_hospedados']:
                    fh=True
            except:
                fh=False      
            try:
                if request.POST['restaurante_reservado']:
                    rr=True
            except:
                rr=False       
            try:                
                viagem=Viagem(        
                    responsavel_viagem=request.POST['responsavel_viagem'],
                    contato_responsavel=validation['contato_responsavel']['celular'],            
                    user=request.user, 
                    dt_Chegada=request.POST['dt_chegada'],
                    dt_Saida=request.POST['dt_saida'],
                    ficarao_hospedados=fh,
                    hotel=request.POST['hotel'],
                    restaurante_reservado=rr,
                    restaurante=request.POST['restaurante'],
                    tipo_veiculo=Tipo_Veiculo.objects.get(id=request.POST['tipo_veiculo']),
                    quant_passageiros=request.POST['quant_passageiros'],
                    empresa_transporte=request.POST['empresa_transporte'],
                    cnpj_empresa_transporte=validation['cnpj_empresa_transporte']['cnpj'],
                    cadastur_empresa_transporte=validation['cadastur_empresa_transporte']['cadastur'],                    
                    obs=request.POST['obs'],
                    estado_origem=Estado.objects.get(id=request.POST['estado']),
                    cidade_origem=Cidade.objects.get(id=request.POST['cidade']),
                    ativo=True)
                viagem.save()    
                          
                if tipo=='turismo':
                    viagem.senha='T'+get_random_string()+str(viagem.id)+get_random_string() 
                    viagem.save()
                    viagem_turismo=Viagem_Turismo(
                        viagem=viagem,
                        outros=request.POST['outros'],
                        nome_guia=request.POST['nome_guia'],
                        cadastur_guia=validation['cadastur_guia']['cadastur'],
                        celular=validation['celular']['celular'],
                        telefone=validation['telefone']['telefone'],
                        ativo=True                         
                    ) 
                    viagem_turismo.save()
                    try:
                        for ponto in request.POST.getlist('pontos_turisticos'):
                            viagem_turismo.pontos_turisticos.add(Pontos_Turisticos.objects.get(nome=ponto))
                        viagem_turismo.save()                    
                    except:
                        pass
                else:
                    viagem.senha='C'+get_random_string()+str(viagem.id)+get_random_string() 
                    viagem.save()
                messages.success(request, 'Viagem cadastrada.')
                return redirect('senhas:cad_transporte')

            except Exception as e:
                print('e:', e, '\nform:', form.errors)
                erro = str(e).split(', ')

                print('erro:', erro)

                if erro[0] == '(1062':
                    messages.error(request, 'Erro: Usuário já existe.')
                else:
                    # Se teve erro:
                    print('Erro: ', form.errors)
                    erro_tmp = str(form.errors)
                    erro_tmp = erro_tmp.replace('<ul class="errorlist">', '')
                    erro_tmp = erro_tmp.replace('</li>', '')
                    erro_tmp = erro_tmp.replace('<ul>', '')
                    erro_tmp = erro_tmp.replace('</ul>', '')
                    erro_tmp = erro_tmp.split('<li>')

                    messages.error(request, erro_tmp[1] + ': ' + erro_tmp[2])
        else:
            messages.error(request, 'Corrigir o erro apresentado.')
        veiculos=Tipo_Veiculo.objects.all()
        pontosTuristicos= Pontos_Turisticos.objects.filter(ativo=True)
    #Incluindo as informações coletas no contexto para uso no Template
        viagem_turismo=False
        if tipo=='turismo':
            viagem_turismo={
                'nome_guia': request.POST['nome_guia'], 
                'cadastur_guia': request.POST['cadastur_guia'],
                'celular': request.POST['celular'],
                'telefone': request.POST['telefone'],
                'outros': request.POST['outros']
            }  
        try:
            estado=Estado.objects.get(id=request.POST['estado'])      
        except:
            estado=''
        try:
            cidade=Cidade.objects.get(id=request.POST['cidade'])
        except:
            cidade=''
        try: 
            if request.POST['ficarao_hospedados']:
                ficarao_hospedados=True
        except:
            ficarao_hospedados=False
        try: 
            if request.POST['restaurante_reservado']:
                restaurante_reservado=True
        except:
            restaurante_reservado=False
        try:
            tipo_veiculo=Tipo_Veiculo.objects.get(id=request.POST['tipo_veiculo'])            
        except:
            tipo_veiculo=''
        pontos_selecionados=[]        
        try:
            for u in request.POST.getlist('pontos_turisticos'):
                pontos_selecionados.append(Pontos_Turisticos.objects.get(nome=u))
        except:
            pass
        context={ 
            'form': form, 
            'validation': validation, 
            'veiculos': veiculos, 
            'pontos': pontosTuristicos,
            'tipo': tipo,
            'titulo': 'CADASTRAR',
            'estado_': estado,
            'estados': estados,  
            'cidade': cidade,
            'viagem': {'responsavel_viagem': request.POST['responsavel_viagem'],
                        'contato_responsavel': request.POST['contato_responsavel'],
                        'dt_Chegada2': request.POST['dt_chegada'],
                       'dt_Saida2': request.POST['dt_saida'],
                    #    'estado_origem': request.POST['estado'],
                    #    'cidade_origem': request.POST['cidade'],
                       'empresa_transporte': request.POST['empresa_transporte'],
                       'cnpj_empresa_transporte': request.POST['cnpj_empresa_transporte'],
                       'cadastur_empresa_transporte': request.POST['cadastur_empresa_transporte'],
                       'quant_passageiros': request.POST['quant_passageiros'],
                       'tipo_veiculo': tipo_veiculo,
                       'obs': request.POST['obs'],
                       'ficarao_hospedados': ficarao_hospedados,
                       'restaurante_reservado': restaurante_reservado,
                       'restaurante': request.POST['restaurante'],
                       'hotel': request.POST['hotel']
                    },                                  
            'viagem_turismo': viagem_turismo,
            'pontos_selecionados': pontos_selecionados
        }
        return render(request, 'senhas/viagem_inclui.html', context)
    else:
        form = ViagemForm()

    #Pegando as devidas informações para os selects do formulario abaixo
    veiculos=Tipo_Veiculo.objects.all()    
    pontosTuristicos= Pontos_Turisticos.objects.filter(ativo=True)
    #Incluindo as informações coletas no contexto para uso no Template
    context={ 
        'form': form, 
        'validation': validation, 
        'veiculos': veiculos, 
        'pontos': pontosTuristicos,
        'tipo': tipo,
        'titulo': 'CADASTRAR',
        'estado_': '',        
        'estados': estados,        
    }
    return render(request, 'senhas/viagem_inclui.html', context)


def viagem(request, id):
    viagem = Viagem.objects.get(senha=id)
    try:
        viagem_turismo = Viagem_Turismo.objects.get(viagem=viagem)
        pontos_turisticos=viagem_turismo.pontos_turisticos.all()
    except:
        viagem_turismo = None
        pontos_turisticos= None
    if not viagem.user == request.user:
        return redirect('senhas:cad_transporte')
    return render(request, 'senhas/viagem.html', { 'viagem': viagem, 'viagem_turismo': viagem_turismo, 'pontos_turisticos': pontos_turisticos })

@login_required
def excluir_viagem(request, id):
    viagem = Viagem.objects.get(senha=id)
    if request.method=='POST':        
        if viagem.user==request.user:
            viagem.ativo=False
            viagem.save()    
            viagem_turismo=Viagem_Turismo.objects.get(viagem=viagem)
            viagem_turismo.ativo=False
            viagem_turismo.save()
            return redirect('senhas:cad_transporte')        
    
    if not viagem.user == request.user:
        return redirect('senhas:cad_transporte')
    return render(request, 'senhas/excluir_senha.html', {'viagem': viagem})

@membro_fiscais_required
def fiscalizar_viagem(request, id):
    viagem = Viagem.objects.get(senha=id)
    try:
        viagem_turismo = Viagem_Turismo.objects.get(viagem=viagem)
        pontos_turisticos=viagem_turismo.pontos_turisticos.all()
    except:
        viagem_turismo = None
        pontos_turisticos= None
    print(request.user.groups)
    return render(request, 'senhas/viagem.html', { 'viagem': viagem, 'viagem_turismo': viagem_turismo, 'pontos_turisticos': pontos_turisticos })

@login_required
def viagem_altera(request, id):
    validation={'veiculo': {'state': True},'quant_passageiros': {'state': True}, 
                'cnpj_empresa_transporte': {'state': True}, 'cadastur_empresa_transporte': {'state': True}, 
                'cadastur_guia':  {'state': True}, 'telefone':  {'state': True}, 
                'celular':{'state': True}, 'chegada_saida':{'state_chegada': True, 'state_saida': True, 'msg': ''},
                'cidade': {'state': True}, 'estado': {'state': True}, 'empresa_transporte': {'state': True},
                'nome_guia':{'state': True}, 'responsavel_viagem':{'state': True}, 'contato_responsavel':{'state': True}} 
    from datetime import date
    tipo=''
    viagem = Viagem.objects.get(senha=id)

    if date.today() > viagem.dt_Saida:
        messages.error(request, 'Não é mais possível alterar viagem, já que a viagem já ocorreu.')
        return redirect('/viagem/' + str(id))


    if viagem.user != request.user:
        messages.error(request, 'Viagem não percente a usuário logado.')
        return redirect('/viagem/' + str(id))


    if request.method == 'POST':        
        form = ViagemForm(request.POST)
        #Aqui a VALIDATION toma novos valores de acordo com o FORM
        if viagem.senha[0]=='T':
            tipo='turismo'
        validation, valido=validationsViagem(request.POST, tipo)           
        if valido:     
            try:
                if request.POST['ficarao_hospedados']:
                    fh=True
            except:
                fh=False  
            try:
                if request.POST['restaurante_reservado']:
                    rr=True
            except:
                rr=False           
            try:        
                viagem.responsavel_viagem=request.POST['responsavel_viagem']
                viagem.contato_responsavel=validation['contato_responsavel']['celular']
                viagem.user=request.user
                viagem.dt_Chegada=request.POST['dt_chegada']
                viagem.dt_Saida=request.POST['dt_saida']
                viagem.ficarao_hospedados=fh
                viagem.hotel=request.POST['hotel']
                viagem.restaurante_reservado=rr
                viagem.restaurante=request.POST['restaurante']
                viagem.tipo_veiculo=Tipo_Veiculo.objects.get(id=request.POST['tipo_veiculo'])
                viagem.quant_passageiros=request.POST['quant_passageiros']
                viagem.empresa_transporte=request.POST['empresa_transporte']
                viagem.cnpj_empresa_transporte=validation['cnpj_empresa_transporte']['cnpj']
                viagem.cadastur_empresa_transporte=request.POST['cadastur_empresa_transporte']
                viagem.obs=request.POST['obs']
                viagem.estado_origem=Estado.objects.get(id=request.POST['estado'])
                viagem.cidade_origem=Cidade.objects.get(id=request.POST['cidade'])
                viagem.save()    
               
                if viagem.senha[0]=='T':                    
                    viagem_turismo=Viagem_Turismo.objects.get(viagem=viagem)
                    
                    viagem_turismo.outros=request.POST['outros']
                    viagem_turismo.nome_guia=request.POST['nome_guia']
                    viagem_turismo.cadastur_guia=request.POST['cadastur_guia']
                    viagem_turismo.celular=validation['celular']['celular']                                              
                    viagem_turismo.telefone=validation['telefone']['telefone']
                    viagem_turismo.pontos_turisticos.clear()
                    viagem_turismo.save()          
                    
                    if request.POST['outros']=='':    
                        viagem_turismo.pontos_turisticos.clear()
                        for ponto in request.POST.getlist('pontos_turisticos'):                                                                        
                            viagem_turismo.pontos_turisticos.add(Pontos_Turisticos.objects.get(nome=ponto))
                        viagem_turismo.save()                                    
                messages.success(request, 'Viagem alterada.')
                return redirect('senhas:cad_transporte')

            except Exception as e:
                print('e:', e)
                messages.error(request, 'Corrigir o erro apresentado.')
                # erro = str(e).split(', ')

                # print('erro:', erro)

                # if erro[0] == '(1062':
                #     messages.error(request, 'Erro: Usuário já existe.')
                # else:
                #     # Se teve erro:
                #     print('Erro: ', form.errors)
                #     erro_tmp = str(form.errors)
                #     erro_tmp = erro_tmp.replace('<ul class="errorlist">', '')
                #     erro_tmp = erro_tmp.replace('</li>', '')
                #     erro_tmp = erro_tmp.replace('<ul>', '')
                #     erro_tmp = erro_tmp.replace('</ul>', '')
                #     erro_tmp = erro_tmp.split('<li>')

                #     messages.error(request, erro_tmp[1] + ': ' + erro_tmp[2])
        else:
            messages.error(request, 'Corrigir o erro apresentado.')
    
    form = ViagemForm(instance=viagem)
    pontosTuristicos_selecionados_=[]
    if viagem.senha[0]=='T':
        tipo='turismo'
        viagem_turismo=Viagem_Turismo.objects.get(viagem=viagem)            
        for u in viagem_turismo.pontos_turisticos.all():
            pontosTuristicos_selecionados_.append(u)
    elif viagem.senha[0]=='C':
        tipo='compras'
        viagem_turismo={}
    veiculos=Tipo_Veiculo.objects.all()
    pontosTuristicos= Pontos_Turisticos.objects.filter(ativo=True)

    estado=viagem.estado_origem
    estados = Estado.objects.all().order_by('nome')
    cidade=viagem.cidade_origem
    #Incluindo as informações coletas no contexto para uso no Template
    # Estado.objects.get()    
    context={ 
        'form': form, 
        'validation': validation,
        'viagem': viagem,
        'viagem_turismo': viagem_turismo,
        'pontos_selecionados': pontosTuristicos_selecionados_,
        'veiculos': veiculos, 
        'pontos': pontosTuristicos,
        'tipo': tipo,
        'titulo': 'ALTERAR',
        'estado_': estado,
        'estados': estados,
        'cidade': cidade        
    }
    
    
    return render(request, 'senhas/viagem_inclui.html', context)

@login_required
def viagem_altera_caledonia(request, id):
    validation={'veiculo': {'state': True},'quant_passageiros': {'state': True}, 
                'cnpj_empresa_transporte': {'state': True}, 'cadastur_empresa_transporte': {'state': True}, 
                'cadastur_guia':  {'state': True}, 'telefone':  {'state': True}, 
                'celular':{'state': True}, 'chegada_saida':{'state_chegada': True, 'state_saida': True, 'msg': ''},
                'cidade': {'state': True}, 'estado': {'state': True}, 'empresa_transporte': {'state': True},
                'nome_guia':{'state': True}, 'responsavel_viagem':{'state': True}, 'contato_responsavel':{'state': True}} 
    from datetime import date
    tipo=''
    viagem = Viagem.objects.get(senha=id)

    if date.today() > viagem.dt_Saida:
        messages.error(request, 'Não é mais possível alterar viagem, já que a viagem já ocorreu.')
        return redirect('/viagem/' + str(id))


    if viagem.user != request.user:
        messages.error(request, 'Viagem não percente a usuário logado.')
        return redirect('/viagem/' + str(id))


    if request.method == 'POST':        
        form = ViagemForm(request.POST)
        #Aqui a VALIDATION toma novos valores de acordo com o FORM
        if viagem.senha[0]=='T':
            tipo='turismo'
        validation, valido=validationsViagem(request.POST, tipo)           
        if valido:     
            try:
                if request.POST['ficarao_hospedados']:
                    fh=True
            except:
                fh=False  
            try:
                if request.POST['restaurante_reservado']:
                    rr=True
            except:
                rr=False           
            try:        
                viagem.responsavel_viagem=request.POST['responsavel_viagem']
                viagem.contato_responsavel=validation['contato_responsavel']['celular']
                viagem.user=request.user
                viagem.dt_Chegada=request.POST['dt_chegada']
                viagem.dt_Saida=request.POST['dt_chegada']
                viagem.ficarao_hospedados=fh
                viagem.hotel=request.POST['hotel']
                viagem.restaurante_reservado=rr
                viagem.restaurante=request.POST['restaurante']
                viagem.tipo_veiculo=Tipo_Veiculo.objects.get(id=request.POST['tipo_veiculo'])
                viagem.quant_passageiros=request.POST['quant_passageiros']
                viagem.empresa_transporte=request.POST['empresa_transporte']
                viagem.cnpj_empresa_transporte=validation['cnpj_empresa_transporte']['cnpj']
                viagem.cadastur_empresa_transporte=request.POST['cadastur_empresa_transporte']
                viagem.obs=request.POST['obs']
                viagem.estado_origem=Estado.objects.get(id=request.POST['estado'])
                viagem.cidade_origem=Cidade.objects.get(id=request.POST['cidade'])
                viagem.save()    
               
                if viagem.senha[0]=='T':                    
                    viagem_turismo=Viagem_Turismo.objects.get(viagem=viagem)
                    
                    viagem_turismo.outros='Pico da Caledônia'
                    viagem_turismo.nome_guia=request.POST['nome_guia']
                    viagem_turismo.cadastur_guia=request.POST['cadastur_guia']
                    viagem_turismo.celular=validation['celular']['celular']                                              
                    viagem_turismo.telefone=validation['telefone']['telefone']
                    viagem_turismo.pontos_turisticos.clear()
                    viagem_turismo.save()          
                                                           
                messages.success(request, 'Viagem alterada.')
                return redirect('senhas:cad_transporte')

            except Exception as e:
                print('e:', e)
                messages.error(request, 'Corrigir o erro apresentado.')
        else:
            messages.error(request, 'Corrigir o erro apresentado.')
    
    form = ViagemForm(instance=viagem)
    pontosTuristicos_selecionados_=[]
    if viagem.senha[0]=='P':
        tipo='turismo'
        viagem_turismo=Viagem_Turismo.objects.get(viagem=viagem)            
        for u in viagem_turismo.pontos_turisticos.all():
            pontosTuristicos_selecionados_.append(u)
    elif viagem.senha[0]=='C':
        tipo='compras'
        viagem_turismo={}
    veiculos=Tipo_Veiculo.objects.all()
    pontosTuristicos= Pontos_Turisticos.objects.filter(ativo=True)

    estado=viagem.estado_origem
    estados = Estado.objects.all().order_by('nome')
    cidade=viagem.cidade_origem
    #Incluindo as informações coletas no contexto para uso no Template
    # Estado.objects.get()    
    context={ 
        'form': form, 
        'validation': validation,
        'viagem': viagem,
        'viagem_turismo': viagem_turismo,
        'pontos_selecionados': pontosTuristicos_selecionados_,
        'veiculos': veiculos, 
        'pontos': pontosTuristicos,
        'tipo': tipo,
        'titulo': 'ALTERAR',
        'estado_': estado,
        'estados': estados,
        'cidade': cidade        
    }
    
    
    return render(request, 'senhas/cadastros/caledonia.html', context)

@login_required
def cad_acesso_ponto(request):

    return render(request, 'senhas/cad_acesso_ponto.html')


def gera_senha_to_html(request, id):

    viagem = Viagem.objects.get(senha=id)
    endereco = 'https://senhas.novafriburgo.rj.gov.br/viagem/fiscalizar/' + str(id)+'/22NF'
    # endereco = 'http://localhost:8000/viagem/fiscalizar/' + str(id)+'/22NF'
    try:
        viagem_turismo = Viagem_Turismo.objects.get(viagem=viagem)
    except:
        viagem_turismo = None
        
    pontosTuristicos_selecionados_=[]
    if viagem.senha[0]=='T':
        tipo='turismo'
        viagem_turismo=Viagem_Turismo.objects.get(viagem=viagem)            
        for u in viagem_turismo.pontos_turisticos.all():
            pontosTuristicos_selecionados_.append(u)
    elif viagem.senha[0]=='C':
        tipo='compras'
        viagem_turismo={}
    veiculos=Tipo_Veiculo.objects.all()
    
    context={
        'viagem': viagem,
        'viagem_turismo': viagem_turismo,
        'pontos_turisticos': pontosTuristicos_selecionados_,
        'endereco': endereco}
    
    return render(request, 'senhas/gera_senha.html', context)

def gera_senha_to_pdf(request, id):
    try:
        url_pdf='/home/turismo/site/turismo/senhas/static/pdf/'+id+'.pdf'    
        # url_pdf='/home/eduardo/projects/turismo/senhas/static/pdf/'+id+'.pdf'    
        pdfkit.from_url('https://senhas.novafriburgo.rj.gov.br/gera_senha_html/'+id+'/22NF', url_pdf)        
        # pdfkit.from_url('http://localhost:8000/gera_senha_html/'+id+'/22NF', url_pdf)        
        context={
            'pdf': url_pdf 
        }
        try:
            return FileResponse(open(url_pdf, 'rb'), content_type='application/pdf')
        except Exception as E:
            print(E)
            raise Http404()
    except Exception as E:
        print(E)
        return redirect('senhas:cad_transporte')
