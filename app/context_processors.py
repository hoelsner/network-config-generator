from app import app
from app.models import Project


@app.context_processor
def inject_all_project_data():
    """
    returns all Project names and ID's from the database to build the sidebar
    :return:
    """
    projects = Project.query.all()
    result = []
    for p in projects:
        p_dict = dict()
        p_dict["id"] = p.id
        p_dict["name"] = p.name
        p_dict["config_templates"] = []

        for cfg in p.configtemplates.all():
            p_dict["config_templates"].append({
                "id": cfg.id,
                "name": cfg.name
            })

        result.append(p_dict)

    return dict(all_project_data=result)
