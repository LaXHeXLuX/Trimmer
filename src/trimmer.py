import bpy
import bmesh

class Trimmer():
    #image_path = ""
    trims = {}
    uv_coords = ""

    @staticmethod
    def compact_points(points):
        def is_collinear(p1, p2, p3):
            return (p2[0] - p1[0]) * (p3[1] - p2[1]) == (p2[1] - p1[1]) * (p3[0] - p2[0])

        if len(points) < 3:
            return points

        compacted = []

        for i in range(len(points)):
            # Get the three points to check
            p1 = points[(i - 1) % len(points)]  # Previous point (wrap around using modulo)
            p2 = points[i]
            p3 = points[(i + 1) % len(points)]  # Next point (wrap around using modulo)

            # Include the point if it's not collinear with its neighbors
            if not is_collinear(p1, p2, p3):
                compacted.append(p2)

        return compacted

    @classmethod
    def test(cls, context, operator):
        operator.report({'INFO'}, "Test button is clicked!")

    @classmethod
    def set_texture(cls, context, operator):
        # Run checks
        obj = context.object
        if obj is None or obj.type != 'MESH' or obj.mode != 'EDIT':
            operator.report({'ERROR'}, "You must be in Edit Mode with a mesh object selected!")
            return

        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            operator.report({'ERROR'}, "The object does not have an active UV map!")
            return

        selected_faces = [face for face in bm.faces if face.select]
        if not selected_faces:
            operator.report({'ERROR'}, "No face selected!")
            return

        # Save UV coordinates
        face = selected_faces[0]
        cls.uv_coords = cls.compact_points([loop[uv_layer].uv.copy() for loop in face.loops])

        operator.report({'INFO'}, f"Coords before: {[loop[uv_layer].uv.copy() for loop in face.loops]}")
        operator.report({'INFO'}, f"Coords after: {cls.uv_coords}")

        # Save image path
        if obj.active_material and obj.active_material.use_nodes:
            nodes = obj.active_material.node_tree.nodes
            found_image_node = False
            for node in nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    found_image_node = True
                    cls.image_path = node.image.filepath
                    break
            if not found_image_node:
                cls.image_path = ""
                operator.report({'WARNING'}, "No texture image found!")
        else:
            cls.image_path = ""
            operator.report({'WARNING'}, "No active material with texture nodes!")

        operator.report({'INFO'}, "UV coordinates and image path saved!")

    @classmethod
    def apply_texture(cls, context, operator):
        if not cls.uv_coords:
            operator.report({'ERROR'}, "No UV data saved! Use 'Set Texture' first.")
            return

        if not cls.image_path:
            operator.report({'ERROR'}, "No image path saved! Use 'Set Texture' first.")
            return

        obj = context.object
        if obj is None or obj.type != 'MESH' or obj.mode != 'EDIT':
            operator.report({'ERROR'}, "You must be in Edit Mode with a mesh object selected!")
            return

        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            operator.report({'ERROR'}, "The object does not have an active UV map!")
            return

        selected_faces = [face for face in bm.faces if face.select]
        if not selected_faces:
            operator.report({'ERROR'}, "No face selected!")
            return

        face = selected_faces[0]
        if len(face.loops) != len(cls.uv_coords):
            operator.report({'ERROR'}, "Selected face must have the same number of vertices as the saved face!")
            return

        # Apply UV coordinates
        for loop, uv in zip(face.loops, cls.uv_coords):
            loop[uv_layer].uv = uv

        bmesh.update_edit_mesh(obj.data)

        # Apply image to material
        material_name = "ImageMaterial"
        material = bpy.data.materials.get(material_name) or bpy.data.materials.new(name=material_name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links

        for node in nodes:
            nodes.remove(node)

        output_node = nodes.new(type="ShaderNodeOutputMaterial")
        output_node.location = (400, 0)

        principled_node = nodes.new(type="ShaderNodeBsdfPrincipled")
        principled_node.location = (0, 0)
        links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

        image_texture_node = nodes.new(type="ShaderNodeTexImage")
        image_texture_node.location = (-400, 0)
        links.new(image_texture_node.outputs['Color'], principled_node.inputs['Base Color'])

        try:
            image_texture_node.image = bpy.data.images.load(cls.image_path)
        except RuntimeError:
            operator.report({'ERROR'}, f"Failed to load image from path: {cls.image_path}")
            return

        if len(obj.data.materials) == 0:
            obj.data.materials.append(material)
        else:
            obj.data.materials[0] = material

        operator.report({'INFO'}, "UV coordinates and texture applied!")

class Trim():
    def __init__(self, uv_coords):
        self.uv_coords = compact_points(uv_coords)

    def compact_points(points):
        def is_collinear(p1, p2, p3):
            return (p2[0] - p1[0]) * (p3[1] - p2[1]) == (p2[1] - p1[1]) * (p3[0] - p2[0])

        if len(points) < 3:
            return points

        compacted = []

        for i in range(len(points)):
            # Get the three points to check
            p1 = points[(i - 1) % len(points)]  # Previous point (wrap around using modulo)
            p2 = points[i]
            p3 = points[(i + 1) % len(points)]  # Next point (wrap around using modulo)

            # Include the point if it's not collinear with its neighbors
            if not is_collinear(p1, p2, p3):
                compacted.append(p2)

        return compacted