import fastapi as fa

import crud.office as co
import models
import schemas.office as so
from core import dependency


router = fa.APIRouter(
    prefix="/offices",
    tags=["offices"],
)


@router.get(
    "/",
    response_model=list[so.Office],
    dependencies=[
        fa.Depends(
            dependency.RoleChecker(
                [models.RoleChoice.ADMIN, models.RoleChoice.STAFF]
            )
        )
    ],
)
async def get_offices(session: dependency.AsyncSessionDepency):
    return await co.Office(session).get_items()


@router.get(
    "/{office_id}/",
    response_model=so.Office,
    dependencies=[
        fa.Depends(
            dependency.RoleChecker(
                [models.RoleChoice.ADMIN, models.RoleChoice.STAFF]
            )
        )
    ],
)
async def get_office_id(
    office_id: int, session: dependency.AsyncSessionDepency
):
    return await co.Office(session).get_item_id(office_id)


@router.post(
    "/",
    response_model=so.OfficeResponse,
    status_code=fa.status.HTTP_201_CREATED,
    dependencies=[
        fa.Depends(
            dependency.RoleChecker(
                [models.RoleChoice.ADMIN, models.RoleChoice.STAFF]
            )
        )
    ],
)
async def create_office(
    session: dependency.AsyncSessionDepency,
    office_data: so.Office,
):
    office = await co.Office(session).create_or_update(
        "create", office_data.model_dump()
    )
    await session.commit()
    await session.refresh(office)
    return office


@router.patch(
    "/{office_id}/",
    response_model=so.UpdateOffice,
    dependencies=[
        fa.Depends(
            dependency.RoleChecker(
                [models.RoleChoice.ADMIN, models.RoleChoice.STAFF]
            )
        )
    ],
)
async def update_office(
    session: dependency.AsyncSessionDepency,
    office_id: int,
    office_data: so.UpdateOffice,
):
    data = office_data.model_dump(exclude_unset=True)
    data["id"] = office_id
    office = await co.Office(session).create_or_update("update", data)
    await session.commit()
    await session.refresh(office)
    return office
