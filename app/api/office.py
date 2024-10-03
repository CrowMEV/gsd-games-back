import fastapi as fa

from core import dependency
from crud import common as common_crud
from crud import office as crud_office
from models import office as model_office
from models import user as model_user
from schemas import office as schema_office


router = fa.APIRouter(
    prefix="/offices",
    tags=["offices"],
)


@router.get(
    "/",
    response_model=list[schema_office.Office],
    dependencies=[
        fa.Depends(
            dependency.RoleChecker(
                [model_user.RoleChoice.ADMIN, model_user.RoleChoice.STAFF]
            )
        )
    ],
)
async def get_offices(session: dependency.AsyncSessionDepency):
    return await common_crud.get_items(session, model_office.Office)


@router.get(
    "/{office_id}",
    response_model=schema_office.Office,
    dependencies=[
        fa.Depends(
            dependency.RoleChecker(
                [model_user.RoleChoice.ADMIN, model_user.RoleChoice.STAFF]
            )
        )
    ],
)
async def get_office_id(
    office_id: int, session: dependency.AsyncSessionDepency
):
    return await common_crud.get_item_id(
        session, model_office.Office, office_id
    )


@router.post(
    "/",
    response_model=schema_office.OfficeResponse,
    status_code=fa.status.HTTP_201_CREATED,
    dependencies=[
        fa.Depends(
            dependency.RoleChecker(
                [model_user.RoleChoice.ADMIN, model_user.RoleChoice.STAFF]
            )
        )
    ],
)
async def create_office(
    session: dependency.AsyncSessionDepency,
    office: schema_office.Office,
):
    data = office.__dict__
    result = await crud_office.create_or_update_office(
        session,
        model_office.Office,
        data,
        common_crud.create_item,  # type:ignore[arg-type]
    )
    return result


@router.patch(
    "/{office_id}",
    response_model=schema_office.UpdateOffice,
    dependencies=[
        fa.Depends(
            dependency.RoleChecker(
                [model_user.RoleChoice.ADMIN, model_user.RoleChoice.STAFF]
            )
        )
    ],
)
async def update_office(
    session: dependency.AsyncSessionDepency,
    office_id: int,
    office_data: schema_office.UpdateOffice,
):
    upload_data = {
        key: value
        for key, value in office_data.__dict__.items()
        if value is not None
    }

    upload_data["id"] = office_id
    result = await crud_office.create_or_update_office(
        session,
        model_office.Office,
        upload_data,
        common_crud.update_item,  # type:ignore[arg-type]
    )
    return result
