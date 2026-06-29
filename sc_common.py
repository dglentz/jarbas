# -*- coding: utf-8 -*-

import math
import itertools
'''
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

Funções geométricas

&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
'''  

def inject_spaceclaim_globals(spaceclaim_globals):
    globals().update(spaceclaim_globals)

# Função para criar um dicionário da face e suas arestas
def store_edges_by_face(faces):
    faceEdgesDict = {}
    try:
        for face in faces:
            edges = get_edges_of_face(face)
            if edges is None:
                raise ValueError("Nenhuma aresta encontrada para a face fornecida.")
            faceEdgesDict[face] = edges
        return faceEdgesDict

    except Exception as e:
        print("Ocorreu um erro ao criar um dicionário da face e suas arestas: {}".format(e))
        return None

def find_unconnected_edge(grupo_arestas, aresta_inicial):
    """Retorna a primeira aresta do grupo que não compartilha vértice com a aresta inicial."""
    try:
        if not grupo_arestas or aresta_inicial is None:
            return None

        vertices_iniciais = [aresta_inicial.Shape.StartVertex, aresta_inicial.Shape.EndVertex]

        for aresta in grupo_arestas:
            if aresta == aresta_inicial:
                continue 

            v_start = aresta.Shape.StartVertex
            v_end = aresta.Shape.EndVertex

            if v_start not in vertices_iniciais and v_end not in vertices_iniciais:
                return aresta  # encontrou uma aresta não conectada

        return None  # nenhuma aresta não conectada foi encontrada
    except Exception as e:
        print("Erro ao buscar aresta não conectada: {}".format(e))
        return None

# Função para medir distância entre vértices
def distance_between_vertices(v1, v2):
    try:
        dist = math.sqrt((v1.X - v2.X)**2 + (v1.Y - v2.Y)**2 + (v1.Z - v2.Z)**2)
        return dist

    except Exception as e:
        print("Não foi possivel medir distância entre vértices: {}".format(e))
        return None

# Função que soma a distancia entre todos os vérices
def total_distance(vertices):
    try:
        if not vertices:
            raise ValueError("A lista de vértices está vazia.")
        
        totalDist = sum(distance_between_vertices(v1, v2) for v1, v2 in itertools.combinations(vertices, 2))
        return totalDist

    except Exception as e:
        print("Não foi possivel medir distância total entre vértices: {}".format(e))
        return None

# Função para remover vértices próximos
def remove_duplicate_vertices(vertices, tolerance=1e-2):
    try:
        if not vertices:
            raise ValueError("A lista de vértices está vazia.")
        
        uniqueVertices = []
        for vertex in vertices:
            if not any(abs(vertex.X - v.X) < tolerance and 
                       abs(vertex.Y - v.Y) < tolerance and 
                       abs(vertex.Z - v.Z) < tolerance for v in uniqueVertices):
                uniqueVertices.append(vertex)

        return uniqueVertices

    except Exception as e:
        print("Não foi possivel remover vértices: {}".format(e))
        return None

# Função para encontrar os 4 vértices das duas extremidades de um tubo quadrado
def separate_end_vertices(vertices):
    # Remove vértices duplicados
    vertices = remove_duplicate_vertices(vertices)
    
    # Encontrar os 4 vértices com a menor distância total entre eles
    endVertices1 = min(itertools.combinations(vertices, 4), key=total_distance)
    
    # Remover os vértices encontrados da lista original
    remainingVertices = [v for v in vertices if v not in endVertices1]
    
    # Encontrar os 4 vértices restantes com a menor distância total entre eles
    endVertices2 = min(itertools.combinations(remainingVertices, 4), key=total_distance)
    
    return list(endVertices1), list(endVertices2)

# Função que extrai os 8 vértices das extremidades de um tubo quadrado e suas arestas 
def extract_vertices_from_body(body):
    centerOfBody = center_body_point(body)
    vertices = []
    edges = []
    
    # Verifica se o corpo tem faces
    if not body.Faces:
        print("Erro: O corpo não tem faces.")
        return [], []
    
    for face in body.Faces:
        faceVertices, faceEdges = extract_face_vertex(face)
        
        # Verifica se a função extract_face_vertex está retornando vértices e arestas
        if not faceVertices:
            print("Ocorreu um erro: {}".format(faceVertices))
        if not faceEdges:
            print("Ocorreu um erro: {}".format(faceEdges))
        
        for vertex in faceVertices:
            if vertex not in vertices:
                vertices.append(vertex)
        for edge in faceEdges:
            if edge not in edges:
                edges.append(edge)
    
    # Verifica se a lista de vértices está vazia
    if not vertices:
        print("Erro: Nenhum vértice foi encontrado.")
        return [], []
    
    # Encontra os 8 vértices mais distantes do centro do corpo
    try:
        vertices.sort(key=key_vertex_distance_from_center(centerOfBody), reverse=True)
    except Exception as e:
        print("Ocorreu um erro: {}".format(e))
        return [], []
    
    vertices = remove_duplicate_vertices(vertices)
    # Seleciona os 8 vértices mais distantes
    farthestVertices = vertices[:8]
    
    return farthestVertices, edges

# Função para criar loft entre duas seleções de linhas
def create_loft_from_pasted_edges(pastedResult1, pastedResult2):
  
    if pastedResult1 is None or pastedResult2 is None:
        print("Erro: Um ou ambos os resultados colados são nulos.")
        return None
    
    try:
        pastedObjects1 = pastedResult1.CreatedObjects
        pastedObjects2 = pastedResult2.CreatedObjects
        
        if not pastedObjects1 or not pastedObjects2:
            print("Erro: Um ou ambos os resultados colados não contêm objetos criados.")
            return None
        
        combinedEdges =[]
        if len(pastedObjects1)>0:
            for edge in pastedObjects1:
                combinedEdges.append(edge)

        if len(pastedObjects2)>0:
            for edge in pastedObjects2:
                combinedEdges.append(edge)
    
        combinedSelection = api_selection_create_diag(combinedEdges)
    
        options = LoftOptions()
        options.GeometryCommandOptions = GeometryCommandOptions()
        
        try:
            result = Loft.Create(combinedSelection, None, options)
        except Exception as e:

            print("Erro ao criar o loft.")
            return None
        
        oExtract = list(result.CreatedBodies)
        converter = DesignFaceConverter(oExtract[0])
        resultBody = converter.converter()
    
        if resultBody is None:
            print("Erro: Não foi possível encontrar o corpo resultante do loft.")
            return None
        
        return resultBody
    except Exception as e:
        print("Ocorreu um erro: {}".format(e))
        return None

# Função para combinar dois corpos
def combine_body(body1, body2):
    try:
        # Verificar se ambos os corpos são instâncias de DesignBody
        if not isinstance(body1, DesignBody) or not isinstance(body2, DesignBody):
            raise ValueError("Ambos os corpos devem ser instâncias de DesignBody.")
        
        # Criar seleções para os corpos
        targets = Selection.Create(body1)
        tools = Selection.Create(body2)
        options = MakeSolidsOptions()
        options.KeepCutter = False
        options.MakeAllRegions = True
        result = Combine.Intersect(targets, tools, options)
        
        return result

    except Exception as e:
        print("Ocorreu um erro ao combinar corpos: {}".format(e))
        return None

def copy_and_paste_edges(selection):
    if selection is None:
        print("Erro: Nenhuma aresta selecionada.")
        return None

    try:
        items = selection.GetItems[IDocObject]()
        if not items:
            print("Erro: Nenhuma aresta selecionada.")
            return None
    except Exception as e:
        print("Ocorreu um erro ao copiar: {}".format(e))

    try:
        result = Copy.Execute(selection)
        if result is None:
            print("Erro ao copiar para a área de transferência.")
            return None

        try:
            if not result.Success:
                print("Erro ao copiar para a área de transferência.")
                return None
        except Exception as e:
            print("Ocorreu um erro ao copiar: {}".format(e))

        return result #pastedSelection
    except Exception as e:
        print("Ocorreu um erro: {}".format(e))
        return None

# Fatiar corpos por plano 
def cut_body_by_plan(bodyIn, plan):

    try:
        selection = Selection.Create(bodyIn)
        datum = Selection.Create(plan)
        result = SplitBody.ByCutter(selection, datum)
        
        oExtract = list(result.CreatedBodies)
        converter = DesignFaceConverter(oExtract[0])
       
        bodyOut1 = converter.converter()

        if bodyOut1 is None:
            raise ValueError("Nenhum corpo foi encontrado após a divisão.")

        # Mede o comprimento das arestas dos tubos
        distEdgebodyOut = get_longest_edge_length(bodyOut1)
        distEdgebodyIn = get_longest_edge_length(bodyIn)

        if distEdgebodyIn > distEdgebodyOut:
            bodyToRemove = bodyOut1
            bodyFinal = bodyIn
        else:
            bodyToRemove = bodyIn
            bodyFinal = bodyOut1

        selection = Selection.Create(bodyToRemove)
        result = Combine.RemoveRegions(selection)

        return bodyFinal

    except Exception as e:
        print("Não foi possivel cortar corpos: {}".format(e))
        return None
 
# Função encontra entre 2 faces a mais proxima em relação a uma lista de faces
def find_closest_face(face1, face2, closeFacesList):
    try:
        # Calcular a área das faces
        areaFace1 = calculate_area_of_face(face1)
        areaFace2 = calculate_area_of_face(face2)
        if areaFace1 is None or areaFace2 is None:
            raise ValueError("Falha ao calcular a área das faces.")

        # Calcular o ponto central das faces 
        findFaceVertex1, findFaceEdgeList1 = extract_face_vertex(face1)            
        centroidFacePoint1 = centroid_vertices(findFaceVertex1)
        findFaceVertex2, findFaceEdgeList2 = extract_face_vertex(face2)            
        centroidFacePoint2 = centroid_vertices(findFaceVertex2)
        if centroidFacePoint1 is None or centroidFacePoint2 is None:
            raise ValueError("Falha ao calcular o ponto central das faces.")

        # Inicializar variáveis para armazenar a face mais próxima e a menor diferença de área
        closest_face = None
        minAreaDiff = float('inf')
        minDistance = float('inf')
        
        for closeFace in closeFacesList:
            # Calcular o ponto central da face de fechamento
            findFaceVertex, findFaceEdgeList = extract_face_vertex(closeFace)            
            centroidCloseFacePoint = centroid_vertices(findFaceVertex)
            if centroidCloseFacePoint is None:
                raise ValueError("Falha ao calcular o ponto central da face de fechamento.")
        
            # Calcular a distância entre os pontos centrais
            distanceToFace1 = dist_between_two_points(centroidFacePoint1, centroidCloseFacePoint)
            distanceToFace2 = dist_between_two_points(centroidFacePoint2, centroidCloseFacePoint)
            if distanceToFace1 is None or distanceToFace2 is None:
                raise ValueError("Falha ao calcular a distância entre os pontos centrais.")
            
            # Calcular a diferença de área
            areaDiff1 = abs(areaFace1 - closeFace.Area)
            areaDiff2 = abs(areaFace2 - closeFace.Area)
            
            # Verificar se a face 3 é mais próxima e tem uma área mais próxima
            if areaDiff1 < minAreaDiff or (areaDiff1 == minAreaDiff and distanceToFace1 < minDistance):
                closest_face = face1
                minAreaDiff = areaDiff1
                minDistance = distanceToFace1
            
            # Verificar se a face 4 é mais próxima e tem uma área mais próxima
            if areaDiff2 < minAreaDiff or (areaDiff2 == minAreaDiff and distanceToFace2 < minDistance):
                closest_face = face2
                minAreaDiff = areaDiff2
                minDistance = distanceToFace2
        
        return closest_face

    except Exception as e:
        print("Erro ao buscar façes próximas: {}".format(e))
        return None

# Função para encontrar arestas equivalentes aos vértices
def find_edges_for_vertices(vertices, edges, onCreate):
    try:
        if not vertices:
            raise ValueError("A lista de vértices está vazia.")
        if not edges:
            raise ValueError("A lista de arestas está vazia.")
        
        relevantEdges = []
        for edge in edges:
            edgeVertices = extract_edge_vertex(edge)
            if edgeVertices is None:
                raise ValueError("Falha ao extrair vértices da aresta.")
            if all(vertex in vertices for vertex in edgeVertices):
                relevantEdges.append(edge)
               
        if len(relevantEdges) == 3 and onCreate == True:
            # Encontrar as duas arestas opostas
            edge1, edge2, edge3 = relevantEdges
            if not (edge1.Shape.StartVertex in [edge2.Shape.StartVertex, edge2.Shape.EndVertex] or
                    edge1.Shape.EndVertex in [edge2.Shape.StartVertex, edge2.Shape.EndVertex]):
                relevantEdges = [edge1, edge2]
            elif not (edge1.Shape.StartVertex in [edge3.Shape.StartVertex, edge3.Shape.EndVertex] or
                      edge1.Shape.EndVertex in [edge3.Shape.StartVertex, edge3.Shape.EndVertex]):
                relevantEdges = [edge1, edge3]
            else:
                relevantEdges = [edge2, edge3]
        
        if len(relevantEdges) not in [2, 4] and onCreate == True:
            return []
      
        return relevantEdges

    except Exception as e:
        print("Não foi possivel encontrar arestas equivalentes aos vértices: {}".format(e))
        return None
 
# Função para criar faces de fechamento em um corpo quadrado
def create_close_body_faces(body,onCreate):
    try:
        # Extrai Lista de vértices e arestas dos corpos
        oListVerticesBody, oListEdgesBody = extract_vertices_from_body(body)
        if oListVerticesBody is None or oListEdgesBody is None:
            raise ValueError("Falha ao extrair vértices ou arestas do corpo.")

        # Extrai lista de vértices das pontas
        oVerticesBodySide1, oVerticesBodySide2 = separate_end_vertices(oListVerticesBody)
        
        if oVerticesBodySide1 is None or oVerticesBodySide2 is None:
            raise ValueError("Falha ao separar vértices das extremidades.")

        # Extrai os edges das extremidades do tubo
        relevantEdgesSide1 = find_edges_for_vertices(oVerticesBodySide1, oListEdgesBody,onCreate)
        relevantEdgesSide2 = find_edges_for_vertices(oVerticesBodySide2, oListEdgesBody,onCreate)
        if relevantEdgesSide1 is None or relevantEdgesSide2 is None:
            raise ValueError("Falha ao encontrar arestas relevantes para os vértices.")
        
        faceSideList = []
        if onCreate == True:
            # Cria a face de fechamento na extremidade do tubo
            faceExtractSide1 = create_surface_from_edges(relevantEdgesSide1)
            faceExtractSide2 = create_surface_from_edges(relevantEdgesSide2)
            
            # Testa as faces válidas para lista de comparação
            if faceExtractSide1 is not None: 
                faceSideList.append(faceExtractSide1)
            if faceExtractSide2 is not None: 
                faceSideList.append(faceExtractSide2)
            
            return faceSideList
        elif onCreate == False:
            return relevantEdgesSide1,relevantEdgesSide2
        
    except Exception as e:
     
        print("Erro ao criar face no fechamento do corpo: {}".format(e))
        return None

# Função de extação do centroide dos vértices
def centroid_vertices(vertices):
    try:
        if not vertices:
            raise ValueError("A lista de vértices está vazia.")
        
        xCoords = [v.X for v in vertices]
        yCoords = [v.Y for v in vertices]
        zCoords = [v.Z for v in vertices]
        
        centroideX = sum(xCoords) / len(vertices)
        centroideY = sum(yCoords) / len(vertices)
        centroideZ = sum(zCoords) / len(vertices)
        
        centroidPoint = Point.Create(centroideX, centroideY, centroideZ) 

        return centroidPoint

    except Exception as e:
        print("Erro ao buscar centroide dos vérices: {}".format(e))
        return None

# Função de extração da lista de vértives de uma aresta
def extract_edge_vertex(edge):
    try:
        listVertex = []
        startVertex = edge.Shape.StartVertex
        endVertex = edge.Shape.EndVertex
        
        if startVertex.Position not in listVertex:
            listVertex.append(startVertex.Position)
        if endVertex.Position not in listVertex:
            listVertex.append(endVertex.Position)
        
        return listVertex

    except Exception as e:
        print("Erro ao encontrar lista de vértices das arestas: {}".format(e))
        return None
    
# Função de extração dos vértices de uma face
def extract_face_vertex(face):
    try:
        listVertex = []
        listEdges = []
        if isinstance(face, DesignFace): 
            faceExtractEdges = face.Edges
            for edge in faceExtractEdges:
                if isinstance(edge, DesignEdge): # pyright: ignore[reportUndefinedVariable]
                    listEdges.append(edge)
                    vertices = extract_edge_vertex(edge)
                    for vertex in vertices:
                        if vertex not in listVertex:
                            listVertex.append(vertex)
        else:
            raise TypeError("O objeto fornecido não é um DesignFace.")
        
        return listVertex, listEdges

    except Exception as e:
        print("Ocorreu um erro ao buscar vértices da face: {}".format(e))
        return None, None

#Função cria face de superficie com arestas como entrada 
def create_surface_from_edges(edges):
    try:
        if len(edges) != 4:
            print("create_surface_from_edges: número de arestas diferente de 4!")
            return None
 
        alignedEdges = sort_by_vertex_share(list(edges))

            
        if alignedEdges is None or len(alignedEdges) != 4:
            print("Arestas não formam um loop fechado!")
            return None
    
        selection = Selection.Create(alignedEdges)
        options = LoftOptions()
        options.GeometryCommandOptions = GeometryCommandOptions()
        options.ExtrudeType = ExtrudeType.ForceIndependent
        selection = Selection.Create(find_unconnected_edge(alignedEdges, alignedEdges[0]),alignedEdges[0])
        result = Loft.Create(selection, None, options)
        oExtract = list(result.CreatedBodies)
        converter = DesignFaceConverter(oExtract[0])
        colectionFece = converter.converter()
        faceExtract = colectionFece.Faces[0]
        return faceExtract
    except Exception as e:
        print("Ocorreu um erro ao criar face na extremidade: {}".format(e))
        return None
    
# Função de extração do centro da face
def extrac_face_center(face):
    try:
        faceGapVertex, faceGapEdgeList = extract_face_vertex(face)        
        facesBodyCenter = centroid_vertices(faceGapVertex)
        return facesBodyCenter
    
    except Exception as e:
        print("Ocorreu um erro ao extrair o centro das faces: {}".format(e))
        return None

# Função para ordenar sequencia de 4 arestas por compartilhamento de vértices
def sort_by_vertex_share(edges):
    try:
        # Converte o Array[DesignEdge] para uma lista Python

        if not edges:
            print("Erro: A lista de arestas está vazia.")
            return None
 
        # Inicia a lista ordenada com a primeira aresta
        ordered_edges = [edges.pop(0)]
        # Continua enquanto houver arestas restantes
        while edges:
            last_edge = ordered_edges[-1]
            last_end_vertex = last_edge.Shape.EndVertex
            # Tenta encontrar a próxima aresta conectada ao último vértice da última aresta
            found = False
            for i, edge in enumerate(edges):
                if edge.Shape.StartVertex == last_end_vertex or edge.Shape.EndVertex == last_end_vertex:
                    # Se a próxima aresta for encontrada, adiciona e remove da lista de arestas restantes
                    ordered_edges.append(edges.pop(i))
                    found = True
                    break
            # Se nenhuma aresta foi encontrada, inverte a busca para conectar no vértice inicial da última aresta
            if not found:
                last_start_vertex = last_edge.Shape.StartVertex
                for i, edge in enumerate(edges):
                    if edge.Shape.StartVertex == last_start_vertex or edge.Shape.EndVertex == last_start_vertex:
                        ordered_edges.append(edges.pop(i))
                        found = True
                        break
 
            # Se não encontrou uma aresta conectada em nenhum dos vértices, termina a função com erro
            if not found:
                print("Erro: Não foi possível ordenar todas as arestas de forma sequencial.")
                return None
 
        # Verifica se o caminho ordenado forma um loop fechado (primeiro e último vértices coincidem)
        first_vertex = ordered_edges[0].Shape.StartVertex
        last_vertex = ordered_edges[-1].Shape.EndVertex
        if first_vertex != last_vertex:
            print("Aviso: As arestas não formam um loop fechado.")
        return ordered_edges
    except Exception as e:
        print("Erro: {}".format(e))
        return None
    
# Função para medir distancia minima entre duas faces
def minimum_dist_between_faces(face1, face2):
    try:
        dist = MeasureHelper.MinDistanceBetweenObjects(face1, face2)
        if dist is not None:
            minDist = dist.Distance
        else:
            minDist = 0
        return minDist

    except Exception as e:
        print("Erro ao medir minima distancia entre faces : {}".format(e))
        return None

def get_face_normal_safe(face):
    """
    Retorna normal de uma DesignFace de forma compatível com execução
    interna no SpaceClaim e também via módulo importado.

    Ordem:
    1) face.GetFaceNormal(0,0), quando disponível;
    2) face.Shape.Geometry.Frame.DirZ, para faces planas;
    3) face.Shape.Geometry.Frame.Axis, fallback;
    """
    if face is None:
        return None

    # Forma original usada quando o script roda direto no SpaceClaim
    try:
        return face.GetFaceNormal(0, 0)
        
    except:
        
        pass

    # Fallback para execução como módulo importado
    try:
        geom = face.Shape.Geometry
        frame = geom.Frame
        try:
            return frame.DirZ
     
        except:
            pass

        try:
            return frame.Axis
        except:
            pass
    except:
        pass

    # Último fallback: tenta propriedades diretas da geometria
    try:
        geom = face.Shape.Geometry
        try:
            return geom.Normal
        except:
            pass
        try:
            return geom.Direction
        except:
            pass
    except:
        pass

    return None


# Função para encontrar direção da normal
def normal_direction(normal):
    try:
        dirX = normal.X
        dirY = normal.Y
        dirZ = normal.Z
        
        # Comparar as magnitudes absolutas das componentes para determinar o eixo dominante
        if abs(dirX) >= abs(dirY) and abs(dirX) >= abs(dirZ):
            if dirX > 0:
                return "+X"
            else:
                return "-X"
        elif abs(dirY) >= abs(dirX) and abs(dirY) >= abs(dirZ):
            if dirY > 0:
                return "+Y"
            else:
                return "-Y"
        elif abs(dirZ) >= abs(dirX) and abs(dirZ) >= abs(dirY):
            if dirZ > 0:
                return "+Z"
            else:
                return "-Z"
        else:
            return "Indeterminado"

    except Exception as e:
        print("Erro ao encontrar normal da face: {}".format(e))
        return "Erro"
    
# Função para extrair centro geométrico do corpo
def center_body_point(body):
    try:
        boundingBox = body.Shape.GetBoundingBox(Matrix.Identity)
        bodyCenter = boundingBox.Center
        if isinstance(bodyCenter,Point):
            return bodyCenter

    except Exception as e:
        print("Erro ao buscar centro do corpo: {}".format(e))
        return None  
    
# Função para criar um plano com base em uma face
def create_plane_from_face(face, faceDirection,offSet):
    try:
        createPlane = None
        # Cria coleção de planos resultantes
        selection = Selection.Create(face)
        plane = DatumPlaneCreator.Create(selection, False, None)
        
        # Converte coleção em datumplane
        colectionPlane = plane.GetCreated[DatumPlane]()
        if not colectionPlane:
            raise ValueError("Nenhum DatumPlane foi criado.")
        
        docPlane = colectionPlane[0]
        if isinstance(docPlane, DatumPlane):
            createPlane = docPlane

        # Definir a direção com base no parâmetro faceDirection
        direction_map = {
            "-X": -Direction.DirX,
            "+X": Direction.DirX,
            "+Y": Direction.DirY,
            "-Y": -Direction.DirY,
            "+Z": Direction.DirZ,
            "-Z": -Direction.DirZ
        }
        
        # Verifica se a direção fornecida é válida
        direction = direction_map.get(faceDirection)
        if direction is None:
            raise ValueError("Direção inválida fornecida: {}".format(faceDirection))
        
        # Seleciona plano criado e desloca para direção informada 
        selection2 = Selection.Create(createPlane)
        options = MoveOptions()
        Move.Translate(selection2, direction, MM(offSet), options)
        
        # Encontra o centro geométrico do plano
        createPlaneCenter = createPlane.Shape.Geometry.Frame.Origin
        
        return createPlane, createPlaneCenter

    except Exception as e:
        print("Erro ao criar plano em uma face: {}".format(e))
        return None, None
    
# Função para dividir faces
def split_faces(face1, face2):
   
    # Verifica se ambas as faces são válidas
    if face1 is None or face2 is None:
        print("Erro: Ambas as faces devem ser válidas e não nulas.")
        return None
    
    try:
        options = SplitFaceOptions()
        selection = api_selection_create_diag(face1)
        cutter = api_selection_create_diag(face2)
        if selection is None or cutter is None:
            return [face1, face1]

        result = SplitFace.ByCutter(selection, cutter, options)

        if not result.Success or len(list(result.CreatedFaces)) == 0:
            print("Erro ao dividir as faces.")
            return [face1,face1]

        created_faces = list(result.CreatedFaces)
        return created_faces

    except Exception as e:
        print("oi")
        print("Ocorreu um erro ao dividir as faces: {}".format(e))
        try:
            return list(result.CreatedFaces)
        except:
            return None
    
# Função de extração das 2 ultimas faces de um corpo
def extract_last_face(body):
    try:
        # Verifica se o objeto é uma instância de DesignBody
        if not isinstance(body, DesignBody):
            raise TypeError("O objeto fornecido não é um DesignBody.")

        # Obtém as faces do corpo
        extract_face = body.Faces

        # Verifica se há pelo menos duas faces
        if extract_face.Count < 2:
            raise ValueError("O corpo deve ter pelo menos duas faces.")

        # Extrai as duas últimas faces
        out_face1 = extract_face[-1]
        out_face2 = extract_face[-2]

        return out_face1, out_face2

    except Exception as e:
        print("Erro inesperado: {}".format(e))
        return None, None
    
# Função para encontrar face mais próxima ou mais distante centro de duas faces em relação a outra
def find_near_close_face(face1, face2, centerReference, MinOrMax):
    try:
     
        # Projetar o ponto central da face de referência nas faces face1 e face2
        pointProject1 = face1.Shape.ProjectPoint(centerReference)
        pointProject2 = face2.Shape.ProjectPoint(centerReference)
        
        # Obter os pontos projetados
        centerFace1 = pointProject1.Point
        centerFace2 = pointProject2.Point
        
        # Calcular as distâncias entre os pontos centrais projetados e o centro da face de referência
        distGapCenterFace1 = dist_between_two_points(centerFace1, centerReference)
        distGapCenterFace2 = dist_between_two_points(centerFace2, centerReference)
        
        # Determinar qual face retornar com base nas distâncias e no valor de MinOrMax
        if (distGapCenterFace1 > distGapCenterFace2 and MinOrMax) or (distGapCenterFace1 < distGapCenterFace2 and not MinOrMax):
            return face2,face1
        elif (distGapCenterFace2 > distGapCenterFace1 and MinOrMax) or (distGapCenterFace2 < distGapCenterFace1 and not MinOrMax):
            return face1,face2
        else:
            # Se as distâncias forem iguais, retornar uma das faces (aqui escolhemos face1 por padrão)
            return face1,face2
        
    except Exception as e:
        print("Ocorreu um erro ao encontrar face: {}".format(e))
        return None,None
    
def create_extra_cut(face_veric, min_distance_face_side):
    try:

        face_center = extrac_face_center(min_distance_face_side)
        edges_to_delete = sort_edges_by_distance(list(face_veric.Edges), face_center)
        edge_lengths = calculate_edge_length(edges_to_delete[0]) 
        new_area = face_veric.Area
        min_area = edge_lengths*4/1000

        if new_area <= min_area:
            delete_itens(edges_to_delete[0])

                
    except Exception as e:
        print("Ocorreu um erro ao processar a face: ",e)

 # Função para ordenar da aresta mais proxima a mais distante em relação a um ponto 

#Função para ordenar arestas em relação a um ponto de referencia
def sort_edges_by_distance(edges, referencePoint):
    # Verificação de entradas nulas ou vazias
    if edges is None or referencePoint is None:
        raise ValueError("edges e referencePoint não podem ser nulos.")
    if not edges:
        raise ValueError("A lista de edges não pode estar vazia.")
    
    # Verificação de tipos
    if not isinstance(edges, list):
        raise TypeError("edges deve ser uma lista.")

    edgeDistances = []
    try:
        for edge in edges:
            midpoint = edge_midpoint(edge)
            distance = dist_between_two_points(midpoint, referencePoint)
            edgeDistances.append((edge, distance))
    except Exception as e:
        print("Erro ao ordenar arestas: {}".format(e))
    
    # Ordenar as arestas pela distância ao ponto de referência usando um processo manual
    try:
        for i in range(len(edgeDistances)):
            minIndex = i
            for j in range(i + 1, len(edgeDistances)):
                if edgeDistances[j][1] < edgeDistances[minIndex][1]:
                    minIndex = j
            edgeDistances[i], edgeDistances[minIndex] = edgeDistances[minIndex], edgeDistances[i]
    except Exception as e:
        print("Erro ao ordenar arestas: {}".format(e))
    
    return [edge for edge, distance in edgeDistances]

# Função para encontrar o ponto central de uma aresta
def edge_midpoint(edge):
    try:
        startPoint = edge.Shape.StartPoint
        endPoint = edge.Shape.EndPoint
        
        midX = (startPoint.X + endPoint.X) / 2
        midY = (startPoint.Y + endPoint.Y) / 2
        midZ = (startPoint.Z + endPoint.Z) / 2
        
        return Point.Create(midX, midY, midZ) 

    except Exception as e:
        print("Ocorreu um erro ao encontrar ponto central de uma aresta: {}".format(e))
        return None
    
# Função para extração de arestas de uma face 
def get_edges_of_face(face):
    try:
        edges = face.Edges
        if edges is None:
            raise ValueError("Nenhuma aresta encontrada na face fornecida.")
        return edges

    except Exception as e:
        print("Ocorreu um erro para extração de arestas de uma face : {}".format(e))
        return None   

'''
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

Funções de Medição

&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
''' 
# Função para calcular comprimento da aresta
def calculate_edge_length(edge):
    try:
        edgeIn = None
        if isinstance(edge, DesignEdge):
            edgeIn = edge
        else:
            raise TypeError("O objeto fornecido não é um DesignEdge.")
        
        return edgeIn.Shape.Length

    except Exception as e:
        print("Ocorreu um para calcular comprimento da aresta: {}".format(e))
        return None

# Função calcula a maior aresta do corpo
def get_longest_edge_length(body):
    try:
        faces = body.Faces
        if faces is None:
            raise ValueError("O corpo não possui faces.")

        faceEdgesDict = store_edges_by_face(faces)
        if faceEdgesDict is None:
            raise ValueError("Falha ao armazenar arestas por face.")

        maxLength = 0
        for edges in faceEdgesDict.values():
            for edge in edges:
                length = calculate_edge_length(edge)
                if length is None:
                    raise ValueError("Falha ao calcular o comprimento da aresta.")
                if length > maxLength:
                    maxLength = length

        return maxLength

    except Exception as e:
        print("Ocorreu um erro para calcular a maior aresta do corpo: {}".format(e))
        return None

# Função para calcular a área de uma face
def calculate_area_of_face(face):
    try:
        area = face.Area
        return area

    except Exception as e:
        print("Ocorreu um erro para calcular a área de uma face: {}".format(e))
        return None

# Mede a distancia entre dois pontos
def dist_between_two_points(point1, point2):
    try:
        dist = math.sqrt((point1.X - point2.X)**2 + (point1.Y - point2.Y)**2 + (point1.Z - point2.Z)**2)
        return round(dist,4)
    except:
        return None
 
# Função para medir angulo entre duas faces
def angle_between_two_faces(face1, face2):
    try:

        normal1 = get_face_normal_safe(face1)
        normal2 = get_face_normal_safe(face2)

        if normal1 is None or normal2 is None:
            raise ValueError("Não foi possível obter a normal de uma das faces.")

        dotProduct = normal1.X * normal2.X + normal1.Y * normal2.Y + normal1.Z * normal2.Z

        magnitude1 = math.sqrt(normal1.X**2 + normal1.Y**2 + normal1.Z**2)
        magnitude2 = math.sqrt(normal2.X**2 + normal2.Y**2 + normal2.Z**2)

        if magnitude1 == 0 or magnitude2 == 0:
            raise ValueError("Magnitude da normal igual a zero.")

        cosAngle = dotProduct / (magnitude1 * magnitude2)
        cosAngle = max(min(cosAngle, 1), -1)

        angleRadians = math.acos(cosAngle)
        angleDegrees = round(math.degrees(angleRadians), 0)

        return angleDegrees

    except Exception as e:
        print("Ocorreu um erro para medir angulo entre duas faces: {}".format(e))
        return None
    
# Função para extrair arestas de um corpo mais proximas de um ponto
def extract_closest_edges(body, referencePoint):
    # Verificação de entradas nulas ou vazias
    if body is None or referencePoint is None:
        raise ValueError("body e referencePoint não podem ser nulos.")
    
    # Verificação de atributos e tipos
    if not hasattr(body, 'Faces'):
        raise TypeError("body deve ter o atributo 'Faces'.")

    edges = []
    try:
        for face in body.Faces:
            for edge in face.Edges:
                if edge not in edges:
                    edges.append(edge)
    except Exception as e:
        print("Ocorreu um erro para extrair arestas de um corpo mais proximas de um ponto: {}".format(e))

    try:
        sortedEdges = sort_edges_by_distance(edges, referencePoint)
    except Exception as e:
        print("Ocorreu um erro para extrair arestas de um corpo mais proximas de um ponto: {}".format(e))

    closestEdges = sortedEdges[:4]
    
    return closestEdges


'''
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

Funções auxiliares 

&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
''' 
def key_vertex_distance_from_center(centerOfBody):
    def _key(v):
        try:
            return (v.Position - centerOfBody).Magnitude
        except:
            return 0
    return _key

# Função busca ultimo corpo e curvas resultantes
def search_last_body():

    try:
        rootPart = GetRootPart()
        allCurves = rootPart.Curves
        return  allCurves

    except Exception as e:
        print("Ocorreu um erro ao buscar ultimo corpo e curvas resultantes: {}".format(e))
        return None
    
# Função para excluir itens
def delete_itens(item):
     if item:
        oSelect = Selection.Create(item)
        try:
            Delete.Execute(oSelect)
        except:
            print("Não foi possivel excluir o item") 

def api_selection_create_diag(items, tag=None):
    try:
        sel = Selection.Create(items)
        return sel
    except Exception as e1:
        print("Ocorreu um erro ao selecionar diretamente: {}".format(e1))

    try:
        if isinstance(items, list) or isinstance(items, tuple):
            sel = Selection.Create(*items)
            return sel
    except Exception as e2:
        print("Ocorreu um erro ao selecionar com star args: {}".format(e2))

    try:
        if isinstance(items, list) or isinstance(items, tuple):
            if len(items) == 1:
                sel = Selection.Create(items[0])
                return sel
    except Exception as e3:
        print("Ocorreu um erro ao selecionar item único: {}".format(e3))

    return None

'''
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

Classes

&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
''' 
class DesignFaceConverter:
    def __init__(self, oInstance):
        self.oInstance = oInstance

    def converter(self):
        oFace = self.oInstance
        if isinstance(oFace, DesignFace):
            oBody = oFace.Parent
            return oBody
        elif isinstance(oFace, DesignBody):
            oBody = oFace
            return oBody
        else:
            oFace = self.oInstance.Master
            if isinstance(oFace, DesignFace):
                oBody = oFace.Parent
                return oBody
            elif isinstance(oFace, DesignBody):
                oBody = oFace
                return oBody
            else:
                raise TypeError("O objeto não é um DesignFace ou DesignGeneralFace")        
            