import fastapi as fa
from sqlalchemy.exc import IntegrityError

import models
import schemas.office as schemas_office
from core import dependency
from services import OfficeService


router = fa.APIRouter(
    prefix="/offices",
    tags=["offices"],
)


@router.get(
    "/",
    response_model=list[schemas_office.OfficeResponse],
    dependencies=[
        fa.Depends(
            dependency.RoleChecker(
                [models.RoleChoice.ADMIN, models.RoleChoice.STAFF]
            )
        )
    ],
)
async def get_offices(session: dependency.AsyncSessionDepency):
    return await OfficeService(session).get_offices()


@router.get(
    "/{office_id}/",
    response_model=schemas_office.OfficeResponse,
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
    return await OfficeService(session).get_office(office_id)


@router.post(
    "/",
    response_model=schemas_office.OfficeResponse,
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
    office_data: schemas_office.Office,
):
    try:
        office = await OfficeService(session).create_office(
            office_data.model_dump()
        )
    except IntegrityError as err:
        if (
            err.orig is not None
            and "address_city_constraint" in err.orig.args[0]
        ):
            raise fa.HTTPException(
                status_code=fa.status.HTTP_409_CONFLICT,
                detail=(
                    f"Office with {office_data.city}, {office_data.address}"
                    f" already exist"
                ),
            ) from err
        raise err
    await session.commit()
    await session.refresh(office)
    return office


@router.patch(
    "/{office_id}/",
    response_model=schemas_office.OfficeResponse,
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
    office_data: schemas_office.UpdateOffice,
):
    data = office_data.model_dump(exclude_unset=True)
    data["id"] = office_id
    try:
        office = await OfficeService(session).update_office(data)
    except IntegrityError as err:
        if (
            err.orig is not None
            and "address_city_constraint" in err.orig.args[0]
        ):
            raise fa.HTTPException(
                status_code=fa.status.HTTP_409_CONFLICT,
                detail=(
                    f"Office with {office_data.city}, {office_data.address}"
                    f" already exist"
                ),
            ) from err
        raise err
    await session.commit()
    await session.refresh(office)
    return office
