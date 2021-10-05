import functools
import globals as g
import functions as f
import supervisely_lib as sly


def send_error_data(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        value = None
        try:
            value = func(*args, **kwargs)
        except Exception as e:
            request_id = kwargs["context"]["request_id"]
            g.my_app.send_response(request_id, data={"error": repr(e)})
        return value

    return wrapper


@g.my_app.callback("smart_segmentation")
@sly.timeit
@send_error_data
def smart_segmentation(api: sly.Api, task_id, context, state, app_logger):
    # x1, y1, x2, y2 = f.get_smart_bbox(context["crop"])
    pos_points, neg_points = f.get_pos_neg_points_list_from_context(context)

    bitmap = f.get_bitmap_from_points(pos_points, neg_points)
    bitmap_origin, bitmap_data = f.unpack_bitmap(bitmap)

    request_id = context["request_id"]
    g.my_app.send_response(request_id, data={"origin": bitmap_origin, "bitmap": bitmap_data, "success": True, "error": None})


def main():
    sly.logger.info("Script arguments", extra={
        "context.teamId": g.TEAM_ID,
        "context.workspaceId": g.WORKSPACE_ID,
        "context.projectId": g.PROJECT_ID
    })

    g.my_app.run()


if __name__ == "__main__":
    sly.main_wrapper("main", main)
