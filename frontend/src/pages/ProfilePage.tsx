import { BasicInfoForm } from '../components/profile/BasicInfoForm'
import { MeasurementsForm } from '../components/profile/MeasurementsForm'
import { StylePreferencesForm } from '../components/profile/StylePreferencesForm'

export function ProfilePage() {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-semibold text-neutral-900">Profile</h1>
      <BasicInfoForm />
      <MeasurementsForm />
      <StylePreferencesForm />
    </div>
  )
}
