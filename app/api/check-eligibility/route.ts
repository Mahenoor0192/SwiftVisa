
import { NextResponse } from "next/server"
import { spawn } from "child_process"
import path from "path"

// Define the structure for the backend user profile
interface BackendUserProfile {
  age: string
  nationality: string
  education: string
  employment: string
  income: string
  visa_type: string
  extra: {
    [key: string]: any
  }
}

// Map frontend visa types to backend categories
const visaTypeToCategory: { [key: string]: string } = {
  "F1 Student": "f1",
  "H1B Work": "h1b",
  "B1/B2 Visitor": "b1b2",
  "K1 Fiance": "k1",
}

// Map frontend field names to backend field names
const fieldNameMapping: { [key: string]: string } = {
  universityAcceptance: "university_acceptance",
  schoolName: "school_name",
  formI20Issued: "i20_issued",
  proofOfFundsAmount: "proof_of_funds_amount",
  testScores: "test_scores",
  jobOffer: "job_offer",
  employerName: "employer_name",
  years_experience: "years_experience",
  degree_equiv: "degree_equiv",
  travelPurpose: "travel_purpose",
  trip_duration_days: "trip_duration_days",
  invitation_host: "invitation_host",
  return_ticket: "return_ticket",
  us_citizen_sponsor: "us_citizen_sponsor",
  met_in_person: "met_in_person",
  relationship_length_months: "relationship_length_months",
  evidence_list: "evidence_list",
  // also include the old fields that were there before
  specialtyOccupation: "specialty_occupation",
  returnTies: "return_ties",
  previousVisits: "previous_visits",
  uscitizenFiance: "us_citizen_sponsor",
  metInPerson: "met_in_person",
  intentToMarry: "intent_to_marry",
}

export async function POST(req: Request) {
  try {
    const formData = await req.json()

    const category = visaTypeToCategory[formData.visaType]
    const extraData: { [key: string]: any } = {}

    // Transform frontend data to backend structure
    for (const key in formData) {
      if (key in fieldNameMapping) {
        extraData[fieldNameMapping[key]] = formData[key]
      } else if (
        key !== "visaType" &&
        key !== "age" &&
        key !== "nationality" &&
        key !== "education" &&
        key !== "employment" &&
        key !== "income"
      ) {
        extraData[key] = formData[key]
      }
    }

    const backendProfile: BackendUserProfile = {
      age: formData.age,
      nationality: formData.nationality,
      education: formData.education,
      employment: formData.employment,
      income: formData.income,
      visa_type: formData.visaType,
      extra: {
        [category]: extraData,
      },
    }

    const pythonScriptPath = path.resolve(
      process.cwd(),
      "SwiftVisa-Backend/src/inference_with_gemini.py"
    )

    const pythonProcess = spawn("python3", [pythonScriptPath], {
      env: {
        ...process.env,
        GOOGLE_API_KEY: process.env.GOOGLE_API_KEY,
      },
    })

    let responseData = ""
    let errorData = ""

    // Send data to python script via stdin
    pythonProcess.stdin.write(JSON.stringify(backendProfile))
    pythonProcess.stdin.end()

    // Collect data from stdout
    for await (const chunk of pythonProcess.stdout) {
      responseData += chunk.toString()
    }

    // Collect data from stderr
    for await (const chunk of pythonProcess.stderr) {
      errorData += chunk.toString()
    }

    const exitCode = await new Promise((resolve) => {
      pythonProcess.on("close", resolve)
    })

    if (exitCode !== 0) {
      console.error(`Python script exited with code ${exitCode}`)
      console.error("Stderr:", errorData)
      return NextResponse.json(
        { error: "Eligibility check failed", details: errorData },
        { status: 500 }
      )
    }

    return NextResponse.json(JSON.parse(responseData))
  } catch (error: any) {
    console.error("Error in eligibility check:", error)
    return NextResponse.json(
      { error: "An unexpected error occurred.", details: error.message },
      { status: 500 }
    )
  }
}
