# -*- coding: utf-8 -*-

import math
import sc_common as com

'''
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

Função reconstruir as duas extremidades do tubo

&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
'''


def inject_spaceclaim_globals(spaceclaim_globals):
    globals().update(spaceclaim_globals)
    com.inject_spaceclaim_globals(spaceclaim_globals)


# ---------------------------------------------------------------------------
# Funções auxiliares não presentes no sc_common
# (serão movidas para sc_common manualmente)
# ---------------------------------------------------------------------------

def MM(val):
    return val / 1000.0


def resolve_for_geometry(obj):
    """Resolve body/face para o objeto geométrico real, preferindo .Master quando disponível."""
    if obj is None:
        return None
    try:
        master = getattr(obj, "Master", None)
        if master is not None:
            return master
    except:
        pass
    return obj


def mark_recon_output_body(body, context):
    try:
        if body is None:
            return False
        try:
            body.SetTextAttribute("ReconRole", "output")
        except:
            pass
        return True
    except Exception as e:
        print("Erro ao marcar body como output: {}".format(e))
        return False


def api_midsurface_aspect_create_diag(body, thickness, tag):
    try:
        sc_obj = globals().get('sc', None)
        if sc_obj is not None:
            return sc_obj.MidSurfaceAspect.Create(body, thickness)
    except:
        pass
    try:
        return MidSurfaceAspect.Create(body, thickness)
    except:
        pass
    try:
        body.MidSurface.SetThickness(thickness)
        return True
    except Exception as e:
        print("Erro ao criar MidSurfaceAspect: {}".format(e))
        return None


def get_length(edge):
    return edge.Shape.Length


def sort_edges(edges, descending=True):
    n = len(edges)
    for i in range(n):
        for j in range(0, n - i - 1):
            if (descending and get_length(edges[j]) < get_length(edges[j + 1])) or \
               (not descending and get_length(edges[j]) > get_length(edges[j + 1])):
                edges[j], edges[j + 1] = edges[j + 1], edges[j]
    return edges


def edge_midpoint_safe(edge):
    try:
        return edge.MidPoint
    except:
        pass
    try:
        return edge.Shape.MidPoint
    except:
        pass
    try:
        sp = edge.StartPoint
        ep = edge.EndPoint
        return Point.Create(
            (sp.X + ep.X) / 2.0,
            (sp.Y + ep.Y) / 2.0,
            (sp.Z + ep.Z) / 2.0,
        )
    except:
        return None


def new_sort_by_vertex_share(edges):
    try:
        if not edges or len(edges) < 2:
            return edges
        edges = list(edges)
        ordered_edges = [edges.pop(0)]
        while edges:
            last_edge = ordered_edges[-1]
            last_vertices = [last_edge.Shape.StartVertex, last_edge.Shape.EndVertex]
            found = False
            for i, edge in enumerate(edges):
                edge_vertices = [edge.Shape.StartVertex, edge.Shape.EndVertex]
                if any(v in last_vertices for v in edge_vertices):
                    ordered_edges.append(edges.pop(i))
                    found = True
                    break
            if not found:
                print("Aviso: segmento desconectado detectado.")
                ordered_edges.append(edges.pop(0))
        return ordered_edges
    except Exception as e:
        print("Erro ao ordenar arestas: {}".format(e))
        return None


def align_edge_loop_to_reference(ref_edges, target_edges):
    """
    Re-rotaciona e/ou reverte target_edges para casar espacialmente com ref_edges.
    Evita o twist do Loft.Create quando os dois loops chegam com offset ou sentido
    de rotacao diferentes.
    """
    try:
        if not ref_edges or not target_edges:
            return target_edges
        if len(ref_edges) != len(target_edges):
            return target_edges
        if len(ref_edges) < 2:
            return target_edges

        ref_mid_0 = edge_midpoint_safe(ref_edges[0])
        if ref_mid_0 is None:
            return target_edges

        best_idx = 0
        best_dist = None
        for i, te in enumerate(target_edges):
            tm = edge_midpoint_safe(te)
            if tm is None:
                continue
            d = com.dist_between_two_points(ref_mid_0, tm)
            if d is None:
                continue
            if best_dist is None or d < best_dist:
                best_dist = d
                best_idx = i

        if best_idx != 0:
            target_edges = list(target_edges[best_idx:]) + list(target_edges[:best_idx])

        ref_mid_1 = edge_midpoint_safe(ref_edges[1])
        tgt_mid_1 = edge_midpoint_safe(target_edges[1])
        tgt_mid_last = edge_midpoint_safe(target_edges[-1])

        if ref_mid_1 is not None and tgt_mid_1 is not None and tgt_mid_last is not None:
            d_forward = com.dist_between_two_points(ref_mid_1, tgt_mid_1)
            d_reverse = com.dist_between_two_points(ref_mid_1, tgt_mid_last)
            if d_forward is not None and d_reverse is not None:
                if d_reverse < d_forward:
                    target_edges = [target_edges[0]] + list(reversed(target_edges[1:]))

        return target_edges

    except Exception as e:
        print("Erro ao alinhar loop de arestas: {}".format(e))
        return target_edges


def find_near_close_face_list(faces, centerReference, MinOrMax):
    try:
        if not faces or len(faces) < 2:
            print("A lista de faces deve conter pelo menos duas faces.")
            return None, None

        reference_face = faces[0]
        closest_face = None
        farthest_face = None
        min_dist = float('inf')
        max_dist = float('-inf')

        for face in faces:
            point_project = face.Shape.ProjectPoint(centerReference)
            center_face = point_project.Point
            dist = com.dist_between_two_points(center_face, centerReference)

            if dist < min_dist:
                min_dist = dist
                closest_face = face
            if dist > max_dist:
                max_dist = dist
                farthest_face = face

        if MinOrMax:
            return closest_face, reference_face
        else:
            return farthest_face, reference_face

    except Exception as e:
        print("Ocorreu um erro ao encontrar a face: {}".format(e))
        return None, None


def extract_edges_within_distance(face, edge_list, centerProfile):
    try:
        matching_edges = set()
        tolerance = com.dist_between_two_points(com.extrac_face_center(face), centerProfile)
        for refEdge in face.Edges:
            refEdgeMidpoint = com.edge_midpoint(refEdge)
            for edge in edge_list:
                edgeMidpoint = edge.Shape.ProjectPoint(refEdgeMidpoint).Point
                dist = com.dist_between_two_points(edgeMidpoint, refEdgeMidpoint)
                if dist <= tolerance + 0.004:
                    matching_edges.add(refEdge)
                    continue
        return list(matching_edges)
    except Exception as e:
        print("Erro ao extrair arestas dentro da distância: {}".format(e))
        return []


def get_connected_tip_edges(edge, all_edges):
    connected_edges = []
    vertices = [edge.Shape.EndVertex, edge.Shape.StartVertex]
    for vertex in vertices:
        for other_edge in all_edges:
            if other_edge == edge:
                continue
            other_edge_list = [other_edge.Shape.EndVertex, other_edge.Shape.StartVertex]
            if vertex in other_edge_list:
                connected_edges.append(other_edge)
    return connected_edges


def extract_no_connect_edges(edges):
    edgeListOut = []
    for edge in edges:
        edgeConnectList = get_connected_tip_edges(edge, edge.GetConnection(1))
        for edgeConnect in edgeConnectList:
            if edgeConnect not in edges:
                edgeListOut.append(edgeConnect)
    edgeListOut = [edge for edge in edgeListOut if len(edge.Faces) != 2]
    return edgeListOut


def repair_faces(face, referenceCenter):
    try:
        oListOfEdge = com.get_edges_of_face(face)
        distComparete = {}
        tempBody = face.Parent
        for edge in oListOfEdge:
            centerEdge = com.edge_midpoint(edge)
            dist = com.dist_between_two_points(centerEdge, referenceCenter)
            distComparete[edge] = dist
        edge = min(distComparete, key=distComparete.get)
        com.delete_itens(edge)
        return [tempBody.Faces[-1], tempBody.Faces[-2]]
    except Exception as e:
        print("repair_faces: Não foi possivel corrigir face selecionada: {}".format(e))


def verify_faces(faces, centerEdgeGroup, minArea):
    try:
        for face in faces:
            if len(face.Edges) == 4 or len(face.Edges) == 3:
                cont = 0
                for edge in face.Edges:
                    if com.calculate_edge_length(edge) < MM(4) and com.calculate_area_of_face(face) < minArea:
                        cont += 1
                if cont >= 1:
                    faces = repair_faces(face, centerEdgeGroup)
        return faces
    except Exception as e:
        print("verify_faces: Erro ao verificar faces: {}".format(e))
        return faces


def dist_minimum_verific(edge, face):
    center_face_cut = com.edge_midpoint(edge)
    cont = 0
    for face in face.AdjacentFaces:
        proj = face.Shape.ProjectPoint(center_face_cut)
        dist = com.dist_between_two_points(center_face_cut, proj.Point) * 1000
        if dist < 4:
            cont += 1
    if cont >= 1:
        return True
    else:
        return False


def create_plane_from_edges(edge1, edge2):
    try:
        selection = Selection.Create(edge1, edge2)
        result = DatumPlaneCreator.Create(selection, True, None)
        colectionPlane = result.GetCreated[DatumPlane]()
        if not colectionPlane:
            raise ValueError("Nenhum DatumPlane foi criado.")
        docPlane = colectionPlane[0]
        if isinstance(docPlane, DatumPlane):
            return docPlane
    except Exception as e:
        print("Erro ao criar plano pelas arestas: {}".format(e))
        return None


def process_face_splits(limit_face, edge_list, center_edge_group, minArea):
    if dist_minimum_verific(edge_list[0], limit_face):
        rest_faces = [limit_face, limit_face]
    else:
        rest_faces = com.split_faces(limit_face, edge_list[0].Faces[0])
        rest_faces = verify_faces(rest_faces, center_edge_group, minArea)

    for edge in edge_list[1:]:
        if len(rest_faces) >= 2:
            face_gap, _ = find_near_close_face_list(rest_faces, center_edge_group, True)
            if face_gap:
                if dist_minimum_verific(edge, face_gap):
                    rest_faces = [face_gap, face_gap]
                else:
                    rest_faces = com.split_faces(face_gap, edge.Faces)
                    rest_faces = verify_faces(rest_faces, center_edge_group, minArea)
        else:
            break

    face_gap, _ = find_near_close_face_list(rest_faces, center_edge_group, True)
    return face_gap


def extract_components(group):
    edge_data, limit_face = group
    edge_list = sort_edges(edge_data[0], descending=False)
    center_edge_group = edge_data[1]
    return limit_face, edge_list, center_edge_group


def main_face_repair(inf_group):
    if len(inf_group) != 2 or len(inf_group[0]) != 2 or len(inf_group[1]) != 2:
        print("Perfil C não possui informações necessárias")
        return

    oLimitFace1, edgeList1, centerEdgeGroup1 = extract_components(inf_group[0])
    oLimitFace2, edgeList2, centerEdgeGroup2 = extract_components(inf_group[1])

    body1 = oLimitFace1.Parent
    body2 = oLimitFace2.Parent

    minArea1 = com.calculate_edge_length(edgeList1[0]) * MM(4)
    minArea2 = com.calculate_edge_length(edgeList1[0]) * MM(4)

    if len(edgeList1) >= 3 and len(edgeList2) >= 3:
        face_gap1 = process_face_splits(oLimitFace1, edgeList1, centerEdgeGroup1, minArea1)
        face_gap2 = process_face_splits(oLimitFace2, edgeList2, centerEdgeGroup2, minArea2)
        if len(edgeList1) == 3:
            edgeListOut = extract_no_connect_edges(edgeList1)
            if len(edgeListOut) == 2:
                createPlan = create_plane_from_edges(edgeListOut[0], edgeListOut[1])
                rest_faces = com.split_faces(face_gap1, createPlan)
                verify_faces(rest_faces, centerEdgeGroup1, minArea1)
                rest_faces = com.split_faces(face_gap2, createPlan)
                verify_faces(rest_faces, centerEdgeGroup2, minArea2)
                com.delete_itens(createPlan)
            else:
                return
    else:
        print("Número de arestas inválido")
        return

    faceToConnect1, _ = find_near_close_face_list(body1.Faces, centerEdgeGroup1, True)
    faceToConnect2, _ = find_near_close_face_list(body2.Faces, centerEdgeGroup2, True)
    return faceToConnect1, faceToConnect2, edgeList1, edgeList2, centerEdgeGroup1, centerEdgeGroup2


# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------

def two_sides(body, inf_group):
    try:
        body_for_geom = resolve_for_geometry(body)
        try:
            espessuraPrincipal = body_for_geom.MidSurface.GetThickness()
        except:
            try:
                espessuraPrincipal = body.MidSurface.GetThickness()
            except:
                espessuraPrincipal = None

        faceToConnect1, faceToConnect2, edgeList1, edgeList2, centerEdgeGroup1, centerEdgeGroup2 = main_face_repair(inf_group)

        edgeListToCopy1 = list(faceToConnect1.Edges)
        edgeListToCopy2 = list(faceToConnect2.Edges)

        if len(edgeList1) == 3 and len(edgeList2) == 3:
            edgeListToCopy1 = extract_edges_within_distance(faceToConnect1, edgeList1, centerEdgeGroup1)
            edgeListToCopy2 = extract_edges_within_distance(faceToConnect2, edgeList2, centerEdgeGroup2)
            edgeListToCopy1 = new_sort_by_vertex_share(edgeListToCopy1)
            edgeListToCopy2 = new_sort_by_vertex_share(edgeListToCopy2)
        else:
            edgeListToCopy1 = new_sort_by_vertex_share(edgeListToCopy1)
            edgeListToCopy2 = new_sort_by_vertex_share(edgeListToCopy2)

        try:
            edgeListToCopy2 = align_edge_loop_to_reference(edgeListToCopy1, edgeListToCopy2)
        except Exception as e:
            print("Erro ao alinhar loop de arestas: {}".format(e))

        selection1 = com.api_selection_create_diag(edgeListToCopy1, 'TWO_SIDES_EDGE_LIST_1')
        pasted_selection1 = com.copy_and_paste_edges(selection1)
        selection2 = com.api_selection_create_diag(edgeListToCopy2, 'TWO_SIDES_EDGE_LIST_2')
        pasted_selection2 = com.copy_and_paste_edges(selection2)

        body_from_loft = com.create_loft_from_pasted_edges(pasted_selection1, pasted_selection2)
        newBody = body_from_loft

        if newBody:
            mark_recon_output_body(newBody, 'TWO_SIDES')
            selection = Selection.Create(newBody)
            options = SetColorOptions()
            options.FaceColorTarget = FaceColorTarget.Body
            ColorHelper.SetColor(selection, options, Color.FromArgb(255, 255, 0, 128))
            if espessuraPrincipal is not None:
                api_midsurface_aspect_create_diag(newBody, espessuraPrincipal, 'TWO_SIDES')

            try:
                parent1 = resolve_for_geometry(faceToConnect1.Parent)
                com.delete_itens(parent1)
            except:
                try:
                    com.delete_itens(faceToConnect1.Parent)
                except Exception as e:
                    print("Erro ao excluir parent1: {}".format(e))

            try:
                parent2 = resolve_for_geometry(faceToConnect2.Parent)
                com.delete_itens(parent2)
            except:
                try:
                    com.delete_itens(faceToConnect2.Parent)
                except Exception as e:
                    print("Erro ao excluir parent2: {}".format(e))

            for curve in GetRootPart().Curves:
                com.delete_itens(curve)

            return True

    except Exception as e:
        print("Erro ao executar two_sides: {}".format(e))


# ============================================================
# MAIN MANUAL - Seleção: 2 faces alvo + arestas abertas do corpo
#
# Ordem da seleção:
#   - 2 faces alvo (uma de cada corpo vizinho)
#   - todas as arestas abertas das 2 extremidades do corpo a reconstruir
#     (4 arestas por extremidade = 8 arestas no total para tubos quadrados)
#
# O main distribui as arestas entre as duas extremidades por proximidade
# a cada face alvo e constrói o inf_group antes de chamar two_sides.
# ============================================================

def _group_edges_by_connectivity(edges):
    """Agrupa arestas em dois conjuntos conectados por vértices compartilhados."""
    if not edges:
        return [], []
    edges = list(edges)
    group1 = [edges.pop(0)]
    changed = True
    while changed:
        changed = False
        remaining = []
        for edge in edges:
            vertices_group = set()
            for e in group1:
                vertices_group.add(e.Shape.StartVertex)
                vertices_group.add(e.Shape.EndVertex)
            if edge.Shape.StartVertex in vertices_group or edge.Shape.EndVertex in vertices_group:
                group1.append(edge)
                changed = True
            else:
                remaining.append(edge)
        edges = remaining
    return group1, edges


def main_function(selection):
    try:
        # ------------------------------------------------------------
        # Entrada esperada:
        #   2 faces alvo (de corpos vizinhos)
        #   arestas abertas das 2 extremidades do corpo a reconstruir
        # ------------------------------------------------------------
        extract = list(selection.GetItems[IDocObject]())

        if len(extract) < 3:
            print("Erro: selecione 2 faces alvo e as arestas abertas do corpo a reconstruir.")
            return False, None

        target_faces = []
        edge_list = []

        for item in extract:
            obj = item
            try:
                if not isinstance(obj, DesignFace) and not isinstance(obj, DesignEdge):
                    obj = item.Master
            except:
                obj = item

            try:
                if isinstance(obj, DesignFace):
                    if len(target_faces) < 2:
                        target_faces.append(obj)
                    else:
                        print("Erro: selecione exatamente 2 faces alvo.")
                        return False, None
                elif isinstance(obj, DesignEdge):
                    edge_list.append(obj)
            except:
                pass

        if len(target_faces) != 2:
            print("Erro: selecione exatamente 2 faces alvo. Encontradas: {}".format(len(target_faces)))
            return False, None

        if len(edge_list) < 2:
            print("Erro: selecione as arestas abertas das extremidades do corpo a reconstruir.")
            return False, None

        # ------------------------------------------------------------
        # Obtém o corpo a reconstruir a partir das arestas
        # ------------------------------------------------------------
        body = None
        try:
            edge_ref_face = list(edge_list[0].Faces)[0]
            try:
                if not isinstance(edge_ref_face, DesignFace):
                    edge_ref_face = edge_ref_face.Master
            except:
                pass
            from sc_common import DesignFaceConverter
            body = DesignFaceConverter(edge_ref_face).converter()
        except:
            try:
                body = list(edge_list[0].Faces)[0].Parent
            except:
                pass

        if body is None:
            print("Erro: não foi possível obter o corpo a partir das arestas selecionadas.")
            return False, None

        # ------------------------------------------------------------
        # Separa arestas em 2 grupos por conectividade
        # ------------------------------------------------------------
        edges_group1, edges_group2 = _group_edges_by_connectivity(edge_list)

        if not edges_group1 or not edges_group2:
            print("Erro: não foi possível separar as arestas em dois grupos distintos.")
            return False, None

        # ------------------------------------------------------------
        # Calcula centroides de cada grupo
        # ------------------------------------------------------------
        def _centroid_from_edges(edges):
            vertices = []
            for edge in edges:
                verts = com.extract_edge_vertex(edge)
                if verts:
                    for v in verts:
                        if v not in vertices:
                            vertices.append(v)
            return com.centroid_vertices(vertices)

        centroid1 = _centroid_from_edges(edges_group1)
        centroid2 = _centroid_from_edges(edges_group2)

        if centroid1 is None or centroid2 is None:
            print("Erro: não foi possível calcular os centroides das extremidades.")
            return False, None

        # ------------------------------------------------------------
        # Associa cada grupo à face alvo mais próxima
        # ------------------------------------------------------------
        target_center_0 = com.extrac_face_center(target_faces[0])
        target_center_1 = com.extrac_face_center(target_faces[1])

        dist_g1_t0 = com.dist_between_two_points(centroid1, target_center_0)
        dist_g1_t1 = com.dist_between_two_points(centroid1, target_center_1)

        if dist_g1_t0 <= dist_g1_t1:
            target_for_group1 = target_faces[0]
            target_for_group2 = target_faces[1]
        else:
            target_for_group1 = target_faces[1]
            target_for_group2 = target_faces[0]
            centroid1, centroid2 = centroid2, centroid1
            edges_group1, edges_group2 = edges_group2, edges_group1

        # ------------------------------------------------------------
        # Copia os corpos alvo e localiza a face equivalente em cada cópia
        # ------------------------------------------------------------
        def _copy_body_and_find_face(target_face):
            target_body_original = None
            try:
                from sc_common import DesignFaceConverter
                target_body_original = DesignFaceConverter(target_face).converter()
            except:
                try:
                    target_body_original = target_face.Parent
                except:
                    pass

            if target_body_original is None:
                print("Erro: não foi possível obter o body pai da face alvo.")
                return None

            target_center_original = com.extrac_face_center(target_face)
            if target_center_original is None:
                print("Erro: não foi possível calcular o centro da face alvo original.")
                return None

            sel = Selection.Create(target_body_original)
            result_copy = Copy.Execute(sel)
            if result_copy is None:
                print("Erro: Copy.Execute retornou None.")
                return None

            copied_body = None
            try:
                created = list(result_copy.CreatedBodies)
                if created:
                    try:
                        from sc_common import DesignFaceConverter
                        copied_body = DesignFaceConverter(created[0]).converter()
                    except:
                        copied_body = created[0]
            except:
                pass

            if copied_body is None:
                try:
                    created = list(result_copy.GetCreated[DesignBody]())
                    if created:
                        copied_body = created[0]
                except:
                    pass

            if copied_body is None:
                print("Erro: não foi possível obter o body copiado.")
                return None

            best_face = None
            best_dist = None
            for face in copied_body.Faces:
                try:
                    copied_center = com.extrac_face_center(face)
                    dist = com.dist_between_two_points(target_center_original, copied_center)
                    if dist is None:
                        continue
                    if best_dist is None or dist < best_dist:
                        best_dist = dist
                        best_face = face
                except:
                    pass

            if best_face is None:
                print("Erro: não foi possível localizar a face equivalente na cópia.")
                return None

            return best_face

        limit_face_copy1 = _copy_body_and_find_face(target_for_group1)
        limit_face_copy2 = _copy_body_and_find_face(target_for_group2)

        if limit_face_copy1 is None or limit_face_copy2 is None:
            print("Erro: não foi possível criar cópias das faces alvo.")
            return False, None

        # ------------------------------------------------------------
        # Monta inf_group e executa two_sides
        # ------------------------------------------------------------
        inf_group = [
            ((edges_group1, centroid1), limit_face_copy1),
            ((edges_group2, centroid2), limit_face_copy2),
        ]

        print("Executando two_sides manual...")
        print("Body a reconstruir: {}".format(body))
        print("Grupo 1: {} arestas | Grupo 2: {} arestas".format(len(edges_group1), len(edges_group2)))

        result_final = two_sides(body, inf_group)
        return result_final, body

    except Exception as e:
        print("Erro na main_function manual: {}".format(e))
        return False, None
