FIND_SCENE_QUERY = """
query FindScene($id: ID!) {
  findScene(id: ID!) {
    title
    details
    studio {
      name
      image_path
    }
    performers {
      name
      image_path
    }
    tags { name }
    files {
      path
      duration
      width
      height
    }
  }
}
"""
