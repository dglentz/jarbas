# -*- coding: utf-8 -*-

import math
import itertools
import sc_common as com

'''
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

Função reconstruir uma extremidade do tubo

&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
''' 


def inject_spaceclaim_globals(spaceclaim_globals):
    globals().update(spaceclaim_globals)
    com.inject_spaceclaim_globals(spaceclaim_globals)


def one_side(body,face, edges, centerEdgeGroup1):
    
    oDesing_Body1 = None
    resulting_bodies = None
    cut_plan1 = None
    cut_plan2 = None 
    cut_plan = None
    min_distance_face_side = None
    
    result_final = False
    try:
        oDesing_Body1 = face.Parent
        oDesing_Body2 = body
        
        # Extrair as faces dos corpos
        oListFacesBody1 = oDesing_Body1.Faces
        oListFacesBody2 = oDesing_Body2.Faces

        min_distance_face_side = com.create_surface_from_edges(edges)
        min_distance_face = face
        faceCenter = com.extrac_face_center(face)
        
        for facebody in oListFacesBody1:
            facebodyCenter = com.extrac_face_center(facebody)
            if faceCenter == facebodyCenter:
                min_distance_face = facebody
                continue

        perpendFaceToFirstFace = None
        ofacelimit1 = None
        ofacelimit2 = None

        # Extrai a primeira face perpendicular a face incial
        faceDist1 = {}
        for facesbody1 in oListFacesBody1:
            anglefaces = com.angle_between_two_faces(facesbody1,min_distance_face)
            distCenterFaces = com.minimum_dist_between_faces(min_distance_face,facesbody1)
            nearFaceVeric = com.minimum_dist_between_faces(min_distance_face_side,facesbody1)
            if (anglefaces != 0 or anglefaces != 180 ) and distCenterFaces == 0 and min_distance_face.ExportIdentifier != facesbody1.ExportIdentifier:
                faceDist1[facesbody1] = nearFaceVeric
                          
        perpendFaceToFirstFace = min(faceDist1, key=faceDist1.get)   
        perpendFaceToFirstFaceNormal = com.normal_direction(com.get_face_normal_safe(perpendFaceToFirstFace))
        
        if perpendFaceToFirstFaceNormal in ["+X", "-X"]:
            perpendFaceToFirstFaceNormal = "X"
        elif perpendFaceToFirstFaceNormal in ["+Y", "-Y"]:
            perpendFaceToFirstFaceNormal = "Y"
        elif perpendFaceToFirstFaceNormal in ["+Z", "-Z"]:
            perpendFaceToFirstFaceNormal = "Z"

        # Encontra uma face paralela oposta para medição

        id1 = int(perpendFaceToFirstFace.ExportIdentifier.replace(':', ''))
        faceDist2 = {}
        for facesbody1 in oListFacesBody1: 
            # Mede angulo entre as faces
            anglefaces = com.angle_between_two_faces(facesbody1,perpendFaceToFirstFace)
            # Mede distancia entre as faces
            minDist = com.minimum_dist_between_faces(facesbody1,perpendFaceToFirstFace)
            # Encontra o centro da face da lista
            id2 = int(facesbody1.ExportIdentifier.replace(':', ''))
            # Mede distancia entre pontos
            if id1 != id2:
                distCenterFaces = com.minimum_dist_between_faces(min_distance_face_side,facesbody1)
                if (anglefaces == 0 or anglefaces == 180 ) and minDist>(5/1000) and min_distance_face_side.ExportIdentifier != facesbody1.ExportIdentifier:
                    perpendOpositiveFaceToFirstFace = facesbody1

        # Encontra a primeira face não paralela
        ofaceNoCutDist1 = {}
        for facesbody2 in oListFacesBody2:
            anglefaces = com.angle_between_two_faces(perpendFaceToFirstFace,facesbody2)
            minDist = com.minimum_dist_between_faces(facesbody2,min_distance_face)
            facesbodyNormal2 = com.normal_direction(com.get_face_normal_safe(facesbody2))
            
            if "+"+perpendFaceToFirstFaceNormal == facesbodyNormal2 or "-"+perpendFaceToFirstFaceNormal == facesbodyNormal2:
                ofaceNoCutDist1[facesbody2] = minDist
                
        ofacenocut1 = min(ofaceNoCutDist1, key=ofaceNoCutDist1.get)   
 
        # Encontra a segunda face não paralela
        ofaceNoCutDist2 = {}
        for facesbody2 in oListFacesBody2:
            anglefaces = com.angle_between_two_faces(ofacenocut1,facesbody2)
            facedist =  com.minimum_dist_between_faces(ofacenocut1,facesbody2)
            minDist = com.minimum_dist_between_faces(facesbody2,min_distance_face_side)
            if (anglefaces == 0 or anglefaces == 180 ) and ofacenocut1.ExportIdentifier != facesbody2.ExportIdentifier and facedist>5/1000:
                ofaceNoCutDist2[facesbody2] = minDist

        ofacenocut2 = min(ofaceNoCutDist2, key=ofaceNoCutDist2.get)   

        # Encontra a face 1 para corte
        for facesbody2 in oListFacesBody2:
            for face in list(facesbody2.AdjacentFaces):
                if face == ofacenocut1:
                    anglefaces = com.angle_between_two_faces(facesbody2,ofacenocut1)
                    
                    try:
                        success, value = facesbody2.TextAttributes.TryGetValue("FaceType")
                    except AttributeError as ae:
                        print("Ocorreu um erro ao acessar os atributos: {}".format(ae))   
                    if 88 <= anglefaces <= 92 and value != "NoUse":
                        ofacelimit1 = facesbody2
                        break    

        # Encontra a face 2 para corte
        for facesbody2 in oListFacesBody2:
             for face in list(facesbody2.AdjacentFaces):
                if face == ofacenocut1:
                    anglefaces = com.angle_between_two_faces(ofacelimit1,facesbody2)
                    facedist =  com.minimum_dist_between_faces(ofacelimit1,facesbody2)
                    if (anglefaces == 0 or anglefaces == 180 ) and ofacelimit1.ExportIdentifier != facesbody2.ExportIdentifier and facedist>5/1000:
                        ofacelimit2 = facesbody2
                        break   
            
        # Extrai a normal da face incial
        facedirection = com.normal_direction(com.get_face_normal_safe(min_distance_face))
        Centro_body_2 = com.center_body_point(oDesing_Body2)
        offSet = 50 
        if facedirection in ["+X", "-X"]:
            cut_plan1, cut_point1 = com.create_plane_from_face(min_distance_face, "+X",offSet)
            cut_plan2, cut_point2 = com.create_plane_from_face(min_distance_face, "-X",offSet)
        elif facedirection in ["+Y", "-Y"]:
            cut_plan1, cut_point1 = com.create_plane_from_face(min_distance_face, "+Y",offSet)
            cut_plan2, cut_point2 = com.create_plane_from_face(min_distance_face, "-Y",offSet)
        elif facedirection in ["+Z", "-Z"]:
            cut_plan1, cut_point1 = com.create_plane_from_face(min_distance_face, "+Z",offSet)
            cut_plan2, cut_point2 = com.create_plane_from_face(min_distance_face, "-Z",offSet)
        
        dist1 = com.dist_between_two_points(cut_point1,Centro_body_2)
        dist2 = com.dist_between_two_points(cut_point2,Centro_body_2)

        delete_cut_plan = None     

        if dist1>dist2:
            cut_plan = cut_plan2
            delete_cut_plan =cut_plan1 
        elif dist2>dist1:
            cut_plan = cut_plan1
            delete_cut_plan =cut_plan2
       
        com.delete_itens(delete_cut_plan)
       
# #################################################################
        # Corta primeira face 
        result = com.split_faces(min_distance_face,ofacelimit1)    
        oface_result1,oface_result2 = com.extract_last_face(oDesing_Body1)
        ofaceGap, ofaceNoGap = com.find_near_close_face(oface_result1, oface_result2, com.extrac_face_center(min_distance_face_side),True)   
        com.create_extra_cut(ofaceGap,ofaceNoGap)
# #################################################################
        # Corta segunda face 
        result = com.split_faces(ofaceGap,ofacelimit2)

        # Extrai as ultimas faces do corpo primário
        resultFace1, resultFace2 = com.extract_last_face(oDesing_Body1)
        startIDFace1 = resultFace1.ExportIdentifier
        startIDFace2 = resultFace2.ExportIdentifier

        # Verifica qual das faces usar para extrair linhas
        ofaceGap,ofaceNoGap = com.find_near_close_face(resultFace1, resultFace2, com.extrac_face_center(min_distance_face_side),True)
        # Testa se sobra não tem aresta menor
        com.create_extra_cut(ofaceNoGap,ofaceGap)
  # #################################################################
  
        # Cria um corte superior para verifcar se existe aresta de 4 mm 
        result = com.split_faces(ofaceGap,ofacenocut1)
        if result is not None:
            resultFaceOut1, resultFaceOut2 = com.extract_last_face(oDesing_Body1)

            if startIDFace1 != resultFaceOut1.ExportIdentifier and startIDFace2 != resultFaceOut2.ExportIdentifier:
                _,ofaceToMeassureEdge = com.find_near_close_face(resultFaceOut1, resultFaceOut2, com.extrac_face_center(min_distance_face_side),True)
                oListOfEdge = com.get_edges_of_face(ofaceToMeassureEdge)
                com.create_extra_cut(ofaceToMeassureEdge,min_distance_face_side)

            # Extrai as ultimas faces do corpo primário
            resultFace1, resultFace2 = com.extract_last_face(oDesing_Body1)
            startIDFace1 = resultFace1.ExportIdentifier
            startIDFace2 = resultFace2.ExportIdentifier

            # Verifica qual das faces usar para extrair linhas
            ofaceGap,ofaceNoGap = com.find_near_close_face(resultFace1, resultFace2, com.extrac_face_center(min_distance_face_side),True)
            com.create_extra_cut(ofaceNoGap,ofaceGap)
    
        # Cria um corte Inferior para verifcar se existe aresta de 4 mm 
        result = com.split_faces(ofaceGap,ofacenocut2)
        if result is not None:
            
            resultFaceOut1, resultFaceOut2 = com.extract_last_face(oDesing_Body1)
            if startIDFace1 != resultFaceOut1.ExportIdentifier and startIDFace2 != resultFaceOut2.ExportIdentifier:
                _,ofaceToMeassureEdge = com.find_near_close_face(resultFaceOut1, resultFaceOut2, com.extrac_face_center(min_distance_face_side),True)
                oListOfEdge2 = com.get_edges_of_face(ofaceToMeassureEdge)
                com.create_extra_cut(ofaceToMeassureEdge,min_distance_face_side)

        # Exclui faces criadas
        try: 
            com.delete_itens(min_distance_face_side.Parent)
        except Exception as e:
            print("Não foi possivel excluir faces: ".format(e)) 

        # Divide o corpo
        resulting_bodies = com.cut_body_by_plan(oDesing_Body2,cut_plan)

        # Exclui planos criados
        try: 
            com.delete_itens(cut_plan)
        except Exception as e:
            print("Não foi possivel excluir sobras: ".format(e))     

        # Verifica face mais proxima do corpo
        oface_result3, oface_result4= com.extract_last_face(oDesing_Body1)          
        oList_vertex_1,oList_edges_1 = com.extract_face_vertex(oface_result3)            
        centroid_face_point1 = com.centroid_vertices(oList_vertex_1)       
        oList_vertex_2,oList_edges_2 = com.extract_face_vertex(oface_result4)            
        centroid_face_point2 = com.centroid_vertices(oList_vertex_2)       
        result_body_center = com.center_body_point(resulting_bodies)

        # Extração do ponto central das faces de fechamento
        closeFacesList = com.create_close_body_faces(resulting_bodies,True)

        findFace = com.find_closest_face(oface_result3, oface_result4, closeFacesList)

        # Ordena e copia as arestas da face encontrada
        findEdgesFace = []
        findEdgesFace = findFace.Edges
        alignedEdges1 = com.sort_by_vertex_share(list(findEdgesFace))
        selection = com.api_selection_create_diag(alignedEdges1)
        pasted_selection1 = com.copy_and_paste_edges(selection)

        pasted_selection2 = None
        oFace_list_pos_cut = []
        oFace_list_pos_cut = resulting_bodies.Faces

        # Extrai o ponto central da face a ser conectada
        findFaceVertex,findFaceEdgeList = com.extract_face_vertex(findFace)            
        centroidFaceFind = com.centroid_vertices(findFaceVertex)

        # Exclui faces criadas
        for faceExclude in closeFacesList:
            try:

                com.delete_itens(faceExclude.Parent)

            except Exception as e:
                print("Não foi possível apagar a face: {}".format(str(e)))
                continue

        listExtractEdges = com.extract_closest_edges(resulting_bodies, centroidFaceFind)
        alignedEdges2 = com.sort_by_vertex_share(listExtractEdges)
        selection = com.api_selection_create_diag(alignedEdges2)
        pasted_selection2 = com.copy_and_paste_edges(selection)
        body_from_loft = com.create_loft_from_pasted_edges(pasted_selection1,pasted_selection2)

        com.combine_body(resulting_bodies,body_from_loft)
        combinedEdgesDell = com.search_last_body()
        
        try:
            com.delete_itens(combinedEdgesDell)
        except Exception as e:
            print("Não foi possivel excluir sobras: ".format(e))     
        
        # Exclui linhas extras
        try:
            result = com.FixExtraEdges.FixSpecific(Selection.Create(resulting_bodies.Edges))
        except Exception as e:
            print("Não foi possivel ou não existem linha para correção: ".format(e))
            
        if len(list(resulting_bodies.Faces)) >4:
             face1, face2 = com.extract_last_face(resulting_bodies)
             face1.SetTextAttribute("FaceType","NoUse")

        # Colorir perfil pronto
        try:
            selection = Selection.Create(resulting_bodies)
            options = SetColorOptions()
            options.FaceColorTarget = FaceColorTarget.Body
            ColorHelper.SetColor(selection, options, Color.FromArgb(255, 0, 0, 255))
        except Exception as e:
            print("Não foi possivel modificar a cor do corpo selecionado: ".format(e))
        
        # Exclui sobras
        
        try:
            if oDesing_Body1 is not None:
                com.delete_itens(oDesing_Body1)
        except Exception as e:
            print("Não foi possivel excluir sobras: ".format(e))          
        
        result_final = True
        
    except Exception as e:
        print("Ocorreu ao criar união entre tubos: {}".format(e))
 
    return result_final,resulting_bodies



# ============================================================
# MAIN MANUAL - Seleção por 2 faces
#
# Ordem da seleção:
#   extract[0] = face pertencente ao body aberto que será reconstruído
#   extract[1] = face alvo de conexão
#
# Chamada final:
#   one_side(oDesing_Body2, oTargetFaceCopy, edge_list, centerEdgeGroup1)
# ============================================================

def main_function(selection):
    try:
        # ------------------------------------------------------------
        # Entrada esperada:
        #   1 face alvo
        #   4 arestas da extremidade do body que será reconstruído
        # ------------------------------------------------------------
        extract = list(selection.GetItems[IDocObject]())

        if len(extract) < 5:
            print("Erro: selecione 1 face alvo e 4 arestas da extremidade.")
            return False, None

        target_face = None
        edge_list = []

        # ------------------------------------------------------------
        # 1) Separar face alvo e arestas.
        #    A seleção vem como IDocObject, então tenta usar Master quando necessário.
        # ------------------------------------------------------------
        for item in extract:
            obj = item

            try:
                if not isinstance(obj, DesignFace) and not isinstance(obj, DesignEdge):
                    obj = item.Master
            except:
                obj = item

            try:
                if isinstance(obj, DesignFace):
                    if target_face is None:
                        target_face = obj
                    else:
                        print("Erro: selecione apenas 1 face alvo.")
                        return False, None

                elif isinstance(obj, DesignEdge):
                    edge_list.append(obj)

            except:
                pass

        if target_face is None:
            print("Erro: nenhuma face alvo foi encontrada na seleção.")
            return False, None

        if len(edge_list) != 4:
            print("Erro: selecione exatamente 4 arestas da extremidade. Quantidade encontrada: {}".format(len(edge_list)))
            return False, None

        # ------------------------------------------------------------
        # 2) Ordenar as 4 arestas da extremidade.
        #    O one_side cria uma surface a partir dessas arestas,
        #    então elas precisam formar loop válido com 4 arestas.
        # ------------------------------------------------------------
        try:
            edge_list = com.sort_by_vertex_share(list(edge_list))
        except Exception as e:
            print("Aviso: falha ao ordenar arestas com sort_by_vertex_share: {}".format(e))

        if edge_list is None or len(edge_list) != 4:
            print("Erro: não foi possível ordenar as 4 arestas da extremidade.")
            return False, None

        # ------------------------------------------------------------
        # 3) Obter o body que será reconstruído a partir das arestas.
        #    Usa uma face conectada à primeira aresta e o DesignFaceConverter.
        # ------------------------------------------------------------
        edge_ref_face = None

        try:
            edge_faces = list(edge_list[0].Faces)
            if len(edge_faces) > 0:
                edge_ref_face = edge_faces[0]
        except:
            pass

        if edge_ref_face is None:
            print("Erro: não foi possível obter a face conectada à primeira aresta selecionada.")
            return False, None

        try:
            if not isinstance(edge_ref_face, DesignFace):
                edge_ref_face = edge_ref_face.Master
        except:
            pass

        oDesing_Body2 = None

        try:
            converter = DesignFaceConverter(edge_ref_face)
            oDesing_Body2 = converter.converter()
        except:
            oDesing_Body2 = None

        if oDesing_Body2 is None:
            try:
                oDesing_Body2 = edge_ref_face.Parent
            except:
                oDesing_Body2 = None

        if oDesing_Body2 is None:
            print("Erro: não foi possível obter o body a partir das arestas selecionadas.")
            return False, None

        # ------------------------------------------------------------
        # 4) Calcular centroide das 4 arestas selecionadas.
        # ------------------------------------------------------------
        vertices = []

        for edge in edge_list:
            try:
                edge_vertices = com.extract_edge_vertex(edge)

                for vertex in edge_vertices:
                    if vertex is not None and vertex not in vertices:
                        vertices.append(vertex)

            except:
                try:
                    p1 = edge.Shape.StartVertex.Position
                    p2 = edge.Shape.EndVertex.Position

                    if p1 is not None and p1 not in vertices:
                        vertices.append(p1)

                    if p2 is not None and p2 not in vertices:
                        vertices.append(p2)
                except:
                    pass

        if len(vertices) == 0:
            print("Erro: não foi possível extrair vértices das arestas selecionadas.")
            return False, None

        centerEdgeGroup1 = com.centroid_vertices(vertices)

        if centerEdgeGroup1 is None:
            print("Erro: não foi possível calcular o centroide das arestas.")
            return False, None

        # ------------------------------------------------------------
        # 5) Copiar o BODY PAI da face alvo.
        #
        # Atenção:
        # Não copiamos apenas a face alvo.
        # O one_side usa face.Parent como oDesing_Body1 e precisa que
        # esse parent tenha as faces perpendiculares/laterais.
        # ------------------------------------------------------------
        oTargetFaceCopy = None
        copied_target_body = None

        try:
            target_body_original = None

            try:
                converter = DesignFaceConverter(target_face)
                target_body_original = converter.converter()
            except:
                target_body_original = None

            if target_body_original is None:
                try:
                    target_body_original = target_face.Parent
                except:
                    target_body_original = None

            if target_body_original is None:
                print("Erro: não foi possível obter o body pai da face alvo.")
                return False, None

            target_center_original = com.extrac_face_center(target_face)

            if target_center_original is None:
                print("Erro: não foi possível calcular o centro da face alvo original.")
                return False, None

            sel_target_body = Selection.Create(target_body_original)
            result_copy = Copy.Execute(sel_target_body)

            if result_copy is None:
                print("Erro: Copy.Execute retornou None ao copiar o body da face alvo.")
                return False, None

            # --------------------------------------------------------
            # 5.1) Tenta obter o body copiado por CreatedBodies.
            # --------------------------------------------------------
            try:
                created_bodies = list(result_copy.CreatedBodies)
                if len(created_bodies) > 0:
                    try:
                        copied_target_body = DesignFaceConverter(created_bodies[0]).converter()
                    except:
                        copied_target_body = created_bodies[0]
            except:
                pass

            # --------------------------------------------------------
            # 5.2) Tenta obter o body copiado por GetCreated[DesignBody]().
            # --------------------------------------------------------
            if copied_target_body is None:
                try:
                    created_bodies = list(result_copy.GetCreated[DesignBody]())
                    if len(created_bodies) > 0:
                        try:
                            copied_target_body = DesignFaceConverter(created_bodies[0]).converter()
                        except:
                            copied_target_body = created_bodies[0]
                except:
                    pass

            # --------------------------------------------------------
            # 5.3) Fallback por CreatedObjects.
            # --------------------------------------------------------
            if copied_target_body is None:
                try:
                    for obj in result_copy.CreatedObjects:
                        try:
                            copied_target_body = DesignFaceConverter(obj).converter()
                            if copied_target_body is not None:
                                break
                        except:
                            pass
                except:
                    pass

            if copied_target_body is None:
                print("Erro: não foi possível obter o body copiado da face alvo.")
                return False, None

            # --------------------------------------------------------
            # 5.4) Dentro do body copiado, localizar a face equivalente
            #      à face alvo original pelo menor afastamento entre centroides.
            # --------------------------------------------------------
            best_face = None
            best_dist = None

            for copied_face in copied_target_body.Faces:
                try:
                    copied_center = com.extrac_face_center(copied_face)
                    dist = com.dist_between_two_points(target_center_original, copied_center)

                    if dist is None:
                        continue

                    if best_dist is None or dist < best_dist:
                        best_dist = dist
                        best_face = copied_face
                except:
                    pass

            if best_face is None:
                print("Erro: não foi possível localizar a face equivalente dentro do body copiado.")
                return False, None

            oTargetFaceCopy = best_face

            try:
                print("Body alvo copiado com faces: {}".format(copied_target_body.Faces.Count))
            except:
                print("Body alvo copiado.")

            print("Distância centro face original -> face copiada: {}".format(best_dist))

        except Exception as e:
            print("Erro ao copiar o body da face alvo: {}".format(e))
            return False, None

        if oTargetFaceCopy is None:
            print("Erro: não foi possível criar uma face alvo copiada válida.")
            return False, None

        # ------------------------------------------------------------
        # 6) Executar one_side com o mesmo contrato original:
        #       body  = body da extremidade selecionada
        #       face  = face alvo, mas dentro de uma cópia do body alvo
        #       edges = 4 arestas selecionadas
        #       centerEdgeGroup1 = centroide das arestas
        # ------------------------------------------------------------
        print("Executando one_side manual...")
        print("Body reconstruído: {}".format(oDesing_Body2))
        print("Body alvo copiado: {}".format(copied_target_body))
        print("Face alvo copiada: {}".format(oTargetFaceCopy))
        print("Arestas selecionadas: {}".format(len(edge_list)))
        print("Centroide calculado: {}".format(centerEdgeGroup1))

        result_final, resulting_bodies = one_side(
            oDesing_Body2,
            oTargetFaceCopy,
            edge_list,
            centerEdgeGroup1
        )

        return result_final, resulting_bodies

    except Exception as e:
        print("Erro na main_function manual: {}".format(e))
        return False, None


