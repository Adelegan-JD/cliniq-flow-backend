from app.database.supabase import supabase
from uuid import uuid4
from datetime import datetime, date
from app.schemas.patient import CreatePatient, UpdatePatient
from typing import Optional

#to auto calculate age from dob
def calculate_age(dob:date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

# the function to create patient
async def create_patient(payload: CreatePatient, current_user: dict):
    """
    Creates a new patient record in the database.
    Args:
        payload: CreatePatient Pydantic model for validation
        current_user: dict with current logged-in officer info
    Returns:
        Inserted patient record
    """

    # check if patient exist 
    existing = supabase.table("patients").select("id").eq(
        "nin", payload.statutory_info.nin
    ).execute()

    if existing.data:
        # Return existing patient info instead of creating duplicate
        return existing.data[0]

    # to flatten nested schema for database
    data = {
        "id": str(uuid4()),  # PID
        "first_name": payload.primary_bio.first_name,
        "last_name": payload.primary_bio.last_name,
        "other_names": payload.primary_bio.other_name,
        "date_of_birth": payload.primary_bio.date_of_birth.isoformat(),
        "age": calculate_age(payload.primary_bio.date_of_birth),
        "gender": payload.primary_bio.gender,
        "civil_status": payload.primary_bio.civil_status,
        "religion": payload.primary_bio.religion,
        "tribe": payload.primary_bio.tribe,
        "passport_photo_url": payload.primary_bio.passport_photo_url,
        # Contact
        "phone_number": payload.contact_info.phone_number,
        "alternative_phone": payload.contact_info.alternative_phone,
        "email": payload.contact_info.email,
        "address": payload.contact_info.address,
        "nationality": payload.contact_info.nationality,
        "state_of_origin": payload.contact_info.state_of_origin,
        "lga": payload.contact_info.lga,
        # Statutory
        "nin": payload.statutory_info.nin if payload.statutory_info else None,
        "nhis_number": payload.statutory_info.nhis_number if payload.statutory_info else None,
        "military_service_number": payload.statutory_info.military_service_number if payload.statutory_info else None,
        "education": payload.statutory_info.education if payload.statutory_info else None,
        # Emergency / Next of Kin
        "next_of_kin_name": payload.next_of_kin.full_name,
        "next_of_kin_relationship": payload.next_of_kin.relationship,
        "next_of_kin_phone": payload.next_of_kin.phone_number,
        "next_of_kin_address": payload.next_of_kin.address,
        # System fields
        "registered_by": current_user["id"],
        "registration_date": datetime.utcnow().isoformat(),
    }

    #insert into supabase
    response = supabase.table("patients").insert(data).execute()

    if response.data is None:
        raise Exception("Failed to create patient")

    return response.data[0]

#function to get patients
async def get_patients(search: Optional[str] = None):
    """
    Returns list of patients, optional search by first_name, last_name, phone.
    """
    query = supabase.table("patients").select("*")

    if search:
        # the .or seraches across multiple fields
        query = query.or_(
            f"first_name.ilike.%{search}%,last_name.ilike.%{search}%,phone_number.ilike.%{search}%"
        )

    response = query.execute()
    return response.data

#function to get one patient
async def get_patient_by_id(patient_id: str):
    response = (
        supabase.table("patients")
        .select("*")
        .eq("id", patient_id)
        .single()
        .execute()
    )

    if response.data is None:
        raise Exception("Patient not found")

    return response.data

#function to update patient data
async def update_patient(patient_id: str, payload: UpdatePatient):
    update_data = payload.dict(exclude_unset=True)

    response = (
        supabase.table("patients")
        .update(update_data)
        .eq("id", patient_id)
        .execute()
    )

    if response.data is None:
        raise Exception("Failed to update patient")

    return response.data[0]