"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Loader2, CheckCircle, AlertCircle } from "lucide-react"

type FormData = {
  visaType: string
  age: string
  nationality: string
  education: string
  employment: string
  income: string
  // F1 Student specific
  universityAcceptance: string
  schoolName: string
  formI20Issued: string
  proofOfFunds: string
  testScores: string
  // H1B specific
  jobOffer: string
  employerName: string
  lca: string
  specialtyOccupation: string
  // B1/B2 specific
  travelPurpose: string
  returnTies: string
  previousVisits: string
  // K1 specific
  uscitizenFiance: string
  metInPerson: string
  intentToMarry: string
}

const initialFormData: FormData = {
  visaType: "",
  age: "",
  nationality: "",
  education: "",
  employment: "",
  income: "",
  universityAcceptance: "",
  schoolName: "",
  formI20Issued: "",
  proofOfFunds: "",
  testScores: "",
  jobOffer: "",
  employerName: "",
  lca: "",
  specialtyOccupation: "",
  travelPurpose: "",
  returnTies: "",
  previousVisits: "",
  uscitizenFiance: "",
  metInPerson: "",
  intentToMarry: "",
}

export function EligibilityFormClient() {
  const [formData, setFormData] = useState<FormData>(initialFormData)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [result, setResult] = useState<{ eligible: boolean; message: string } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setResult(null)

    // Build the profile data based on visa type
    const profileData = {
      visa_type: formData.visaType,
      age: formData.age,
      nationality: formData.nationality,
      education: formData.education,
      employment: formData.employment,
      income: formData.income,
      ...(formData.visaType === "F1 Student" && {
        university_acceptance: formData.universityAcceptance,
        school_name: formData.schoolName,
        form_i20_issued: formData.formI20Issued,
        proof_of_funds: formData.proofOfFunds,
        test_scores: formData.testScores,
      }),
      ...(formData.visaType === "H1B Work" && {
        job_offer: formData.jobOffer,
        employer_name: formData.employerName,
        lca: formData.lca,
        specialty_occupation: formData.specialtyOccupation,
      }),
      ...(formData.visaType === "B1/B2 Visitor" && {
        travel_purpose: formData.travelPurpose,
        return_ties: formData.returnTies,
        previous_visits: formData.previousVisits,
      }),
      ...(formData.visaType === "K1 Fiance" && {
        uscitizen_fiance: formData.uscitizenFiance,
        met_in_person: formData.metInPerson,
        intent_to_marry: formData.intentToMarry,
      }),
    }

    console.log("Eligibility Check Payload:", JSON.stringify(profileData, null, 2))

    // TODO: Replace with actual API call to your backend
    // Example: const response = await fetch('YOUR_BACKEND_URL/api/evaluate', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(profileData),
    // })

    // Simulated response
    setTimeout(() => {
      setIsSubmitting(false)
      setResult({
        eligible: true,
        message:
          "Based on your profile, you appear to meet the basic requirements. Please consult with an immigration attorney for a complete assessment.",
      })
    }, 2000)
  }

  const updateField = (field: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <Card className="border-border/60">
      <CardHeader>
        <CardTitle>Visa Eligibility Assessment</CardTitle>
        <CardDescription>
          Provide basic profile information and visa type; we'll ask for any missing details if needed.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Visa Type Selection */}
          <div className="space-y-2">
            <Label htmlFor="visaType">Select visa type</Label>
            <Select value={formData.visaType} onValueChange={(value) => updateField("visaType", value)}>
              <SelectTrigger id="visaType">
                <SelectValue placeholder="Select visa type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="F1 Student">F1 Student</SelectItem>
                <SelectItem value="H1B Work">H1B Work</SelectItem>
                <SelectItem value="B1/B2 Visitor">B1/B2 Visitor</SelectItem>
                <SelectItem value="K1 Fiance">K1 Fiance</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Basic Profile Fields */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="age">Age</Label>
              <Input
                id="age"
                type="number"
                placeholder="Enter your age"
                value={formData.age}
                onChange={(e) => updateField("age", e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="nationality">Nationality</Label>
              <Input
                id="nationality"
                placeholder="Enter your nationality"
                value={formData.nationality}
                onChange={(e) => updateField("nationality", e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="education">Education</Label>
            <Input
              id="education"
              placeholder="Highest level of education"
              value={formData.education}
              onChange={(e) => updateField("education", e.target.value)}
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="employment">Employment</Label>
              <Input
                id="employment"
                placeholder="Current employment status"
                value={formData.employment}
                onChange={(e) => updateField("employment", e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="income">Income</Label>
              <Input
                id="income"
                placeholder="Annual income"
                value={formData.income}
                onChange={(e) => updateField("income", e.target.value)}
              />
            </div>
          </div>

          {/* F1 Student Specific Fields */}
          {formData.visaType === "F1 Student" && (
            <div className="space-y-4 rounded-lg border border-primary/20 bg-primary/5 p-4">
              <h3 className="font-semibold text-primary">F1 Student Visa-specific fields</h3>

              <div className="space-y-2">
                <Label htmlFor="universityAcceptance">University acceptance?</Label>
                <Select
                  value={formData.universityAcceptance}
                  onValueChange={(value) => updateField("universityAcceptance", value)}
                >
                  <SelectTrigger id="universityAcceptance">
                    <SelectValue placeholder="Select option" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Unknown">Unknown</SelectItem>
                    <SelectItem value="Yes">Yes</SelectItem>
                    <SelectItem value="No">No</SelectItem>
                    <SelectItem value="Pending">Pending</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="schoolName">School / University name</Label>
                <Input
                  id="schoolName"
                  placeholder="Enter school or university name"
                  value={formData.schoolName}
                  onChange={(e) => updateField("schoolName", e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="formI20Issued">Is Form I-20 issued?</Label>
                <Select value={formData.formI20Issued} onValueChange={(value) => updateField("formI20Issued", value)}>
                  <SelectTrigger id="formI20Issued">
                    <SelectValue placeholder="Select option" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Unknown">Unknown</SelectItem>
                    <SelectItem value="Yes">Yes</SelectItem>
                    <SelectItem value="No">No</SelectItem>
                    <SelectItem value="Pending">Pending</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="proofOfFunds">Proof of funds amount (currency & amount)</Label>
                <Input
                  id="proofOfFunds"
                  placeholder="e.g., USD 50,000"
                  value={formData.proofOfFunds}
                  onChange={(e) => updateField("proofOfFunds", e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="testScores">Test scores (TOEFL/IELTS/etc)</Label>
                <Input
                  id="testScores"
                  placeholder="e.g., TOEFL 100, IELTS 7.5"
                  value={formData.testScores}
                  onChange={(e) => updateField("testScores", e.target.value)}
                />
              </div>
            </div>
          )}

          {/* H1B Work Specific Fields */}
          {formData.visaType === "H1B Work" && (
            <div className="space-y-4 rounded-lg border border-primary/20 bg-primary/5 p-4">
              <h3 className="font-semibold text-primary">H1B Work Visa-specific fields</h3>

              <div className="space-y-2">
                <Label htmlFor="jobOffer">Job offer from US employer?</Label>
                <Select value={formData.jobOffer} onValueChange={(value) => updateField("jobOffer", value)}>
                  <SelectTrigger id="jobOffer">
                    <SelectValue placeholder="Select option" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Unknown">Unknown</SelectItem>
                    <SelectItem value="Yes">Yes</SelectItem>
                    <SelectItem value="No">No</SelectItem>
                    <SelectItem value="Pending">Pending</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="employerName">Employer name</Label>
                <Input
                  id="employerName"
                  placeholder="Enter employer name"
                  value={formData.employerName}
                  onChange={(e) => updateField("employerName", e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="lca">Labor Condition Application (LCA) filed?</Label>
                <Select value={formData.lca} onValueChange={(value) => updateField("lca", value)}>
                  <SelectTrigger id="lca">
                    <SelectValue placeholder="Select option" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Unknown">Unknown</SelectItem>
                    <SelectItem value="Yes">Yes</SelectItem>
                    <SelectItem value="No">No</SelectItem>
                    <SelectItem value="Pending">Pending</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="specialtyOccupation">Specialty occupation?</Label>
                <Input
                  id="specialtyOccupation"
                  placeholder="Describe your specialty occupation"
                  value={formData.specialtyOccupation}
                  onChange={(e) => updateField("specialtyOccupation", e.target.value)}
                />
              </div>
            </div>
          )}

          {/* B1/B2 Visitor Specific Fields */}
          {formData.visaType === "B1/B2 Visitor" && (
            <div className="space-y-4 rounded-lg border border-primary/20 bg-primary/5 p-4">
              <h3 className="font-semibold text-primary">B1/B2 Visitor Visa-specific fields</h3>

              <div className="space-y-2">
                <Label htmlFor="travelPurpose">Purpose of travel</Label>
                <Select value={formData.travelPurpose} onValueChange={(value) => updateField("travelPurpose", value)}>
                  <SelectTrigger id="travelPurpose">
                    <SelectValue placeholder="Select purpose" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Tourism">Tourism</SelectItem>
                    <SelectItem value="Business">Business</SelectItem>
                    <SelectItem value="Medical">Medical Treatment</SelectItem>
                    <SelectItem value="Conference">Conference/Event</SelectItem>
                    <SelectItem value="Family Visit">Family Visit</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="returnTies">Strong ties to home country?</Label>
                <Select value={formData.returnTies} onValueChange={(value) => updateField("returnTies", value)}>
                  <SelectTrigger id="returnTies">
                    <SelectValue placeholder="Select option" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Unknown">Unknown</SelectItem>
                    <SelectItem value="Yes">Yes</SelectItem>
                    <SelectItem value="No">No</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="previousVisits">Previous US visits</Label>
                <Input
                  id="previousVisits"
                  placeholder="Number of previous visits"
                  value={formData.previousVisits}
                  onChange={(e) => updateField("previousVisits", e.target.value)}
                />
              </div>
            </div>
          )}

          {/* K1 Fiance Specific Fields */}
          {formData.visaType === "K1 Fiance" && (
            <div className="space-y-4 rounded-lg border border-primary/20 bg-primary/5 p-4">
              <h3 className="font-semibold text-primary">K1 Fiance Visa-specific fields</h3>

              <div className="space-y-2">
                <Label htmlFor="uscitizenFiance">Is your fiance a US citizen?</Label>
                <Select
                  value={formData.uscitizenFiance}
                  onValueChange={(value) => updateField("uscitizenFiance", value)}
                >
                  <SelectTrigger id="uscitizenFiance">
                    <SelectValue placeholder="Select option" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Unknown">Unknown</SelectItem>
                    <SelectItem value="Yes">Yes</SelectItem>
                    <SelectItem value="No">No</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="metInPerson">Have you met in person within 2 years?</Label>
                <Select value={formData.metInPerson} onValueChange={(value) => updateField("metInPerson", value)}>
                  <SelectTrigger id="metInPerson">
                    <SelectValue placeholder="Select option" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Unknown">Unknown</SelectItem>
                    <SelectItem value="Yes">Yes</SelectItem>
                    <SelectItem value="No">No</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="intentToMarry">Intent to marry within 90 days?</Label>
                <Select value={formData.intentToMarry} onValueChange={(value) => updateField("intentToMarry", value)}>
                  <SelectTrigger id="intentToMarry">
                    <SelectValue placeholder="Select option" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Unknown">Unknown</SelectItem>
                    <SelectItem value="Yes">Yes</SelectItem>
                    <SelectItem value="No">No</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <Button type="submit" className="w-full" size="lg" disabled={isSubmitting || !formData.visaType}>
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing Eligibility...
              </>
            ) : (
              "Check Eligibility"
            )}
          </Button>

          {/* Result Display */}
          {result && (
            <div
              className={`mt-4 rounded-lg border p-4 ${
                result.eligible
                  ? "border-green-200 bg-green-50 text-green-800"
                  : "border-red-200 bg-red-50 text-red-800"
              }`}
            >
              <div className="flex items-start gap-3">
                {result.eligible ? (
                  <CheckCircle className="h-5 w-5 mt-0.5 text-green-600" />
                ) : (
                  <AlertCircle className="h-5 w-5 mt-0.5 text-red-600" />
                )}
                <div>
                  <h4 className="font-semibold">{result.eligible ? "Potentially Eligible" : "May Not Be Eligible"}</h4>
                  <p className="mt-1 text-sm">{result.message}</p>
                </div>
              </div>
            </div>
          )}
        </form>
      </CardContent>
    </Card>
  )
}
