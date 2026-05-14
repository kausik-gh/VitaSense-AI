import {
  Activity,
  AlertTriangle,
  Brain,
  CalendarDays,
  CheckCircle,
  ChevronLeft,
  ChevronRight,
  CloudSun,
  HeartPulse,
  Loader2,
  Save,
  Smartphone,
  Utensils,
} from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
import type { ElementType, ReactNode } from 'react';
import { useEffect, useMemo, useState } from 'react';
import { fetchDailyLog, saveDailyLog } from '../lib/api';
import type { DailyLogPayload, DailyLogResponse } from '../lib/api';
import { DEMO_USER_ID } from '../lib/demoData';

const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const monthLabel = 'October 2025';
const monthNumber = '10';
const yearNumber = '2025';
const blankDaysBeforeMonth = 2;
const daysInMonth = 31;

const energyOptions = ['Very Low', 'Low', 'Moderate', 'Good', 'High'];
const moodOptions = ['Very Sad', 'Sad', 'Neutral', 'Happy', 'Very Happy', 'Anxious', 'Stressed', 'Exhausted'];
const workloadOptions = ['Very Low', 'Low', 'Moderate', 'High', 'Extreme'];

type FormState = {
  breakfastLog: string;
  lunchLog: string;
  dinnerLog: string;
  snacksBeveragesLog: string;
  ateFromOutside: string;
  processedFoodConsumed: string;
  unusualFoodExposure: string;
  unusualExposureNotes: string;
  energyLevel: string;
  moodToday: string;
  overallMentalFeeling: string;
  emotionalPhysicalImpact: string;
  physicalDiscomfortNotes: string;
  unusualBodyObservation: string;
  dailyEvents: string;
  workloadIntensity: string;
  crowdedPlaceExposure: string;
  travelToday: string;
  emotionalEventNotes: string;
  chatbotSymptomsReported: string;
  doctorConsultedToday: string;
  medicalVisitReason: string;
};

const initialForm: FormState = {
  breakfastLog: '',
  lunchLog: '',
  dinnerLog: '',
  snacksBeveragesLog: '',
  ateFromOutside: '',
  processedFoodConsumed: '',
  unusualFoodExposure: '',
  unusualExposureNotes: '',
  energyLevel: '',
  moodToday: '',
  overallMentalFeeling: '',
  emotionalPhysicalImpact: '',
  physicalDiscomfortNotes: '',
  unusualBodyObservation: '',
  dailyEvents: '',
  workloadIntensity: '',
  crowdedPlaceExposure: '',
  travelToday: '',
  emotionalEventNotes: '',
  chatbotSymptomsReported: '',
  doctorConsultedToday: '',
  medicalVisitReason: '',
};

function nullableText(value: string): string | null {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function splitList(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function boolFromSelect(value: string): boolean | null {
  if (value === 'yes') return true;
  if (value === 'no') return false;
  return null;
}

function dateForDay(day: number): string {
  return `${yearNumber}-${monthNumber}-${String(day).padStart(2, '0')}`;
}

function readString(row: Record<string, unknown>, key: string, fallbackKey?: string): string {
  const value = row[key] ?? (fallbackKey ? row[fallbackKey] : undefined);
  return typeof value === 'string' ? value : '';
}

function readBool(row: Record<string, unknown>, key: string, fallbackKey?: string): string {
  const value = row[key] ?? (fallbackKey ? row[fallbackKey] : undefined);
  if (value === true) return 'yes';
  if (value === false) return 'no';
  return '';
}

function readList(row: Record<string, unknown>, key: string, fallbackKey?: string): string {
  const value = row[key] ?? (fallbackKey ? row[fallbackKey] : undefined);
  return Array.isArray(value) ? value.filter((item) => typeof item === 'string').join(', ') : '';
}

function formFromResponse(response: DailyLogResponse): FormState {
  const memory = response.tables.daily_user_memory_logs ?? {};
  return {
    breakfastLog: readString(memory, 'breakfast_log', 'breakfast'),
    lunchLog: readString(memory, 'lunch_log', 'lunch'),
    dinnerLog: readString(memory, 'dinner_log', 'dinner'),
    snacksBeveragesLog: readString(memory, 'snacks_beverages_log', 'snacks'),
    ateFromOutside: readBool(memory, 'ate_from_outside'),
    processedFoodConsumed: readBool(memory, 'processed_food_consumed'),
    unusualFoodExposure: readBool(memory, 'unusual_food_exposure'),
    unusualExposureNotes: readString(memory, 'unusual_exposure_notes'),
    energyLevel: readString(memory, 'energy_level'),
    moodToday: readString(memory, 'mood_today'),
    overallMentalFeeling: readString(memory, 'overall_mental_feeling'),
    emotionalPhysicalImpact: readBool(memory, 'emotional_physical_impact'),
    physicalDiscomfortNotes: readString(memory, 'physical_discomfort_notes'),
    unusualBodyObservation: readString(memory, 'unusual_body_observation'),
    dailyEvents: readList(memory, 'daily_events', 'events'),
    workloadIntensity: readString(memory, 'workload_intensity'),
    crowdedPlaceExposure: readBool(memory, 'crowded_place_exposure'),
    travelToday: readBool(memory, 'travel_today'),
    emotionalEventNotes: readString(memory, 'emotional_event_notes'),
    chatbotSymptomsReported: readList(memory, 'chatbot_symptoms_reported', 'chatbot_symptoms'),
    doctorConsultedToday: readBool(memory, 'doctor_consulted_today', 'doctor_visit'),
    medicalVisitReason: readString(memory, 'medical_visit_reason'),
  };
}

function buildPayload(logDate: string, form: FormState): DailyLogPayload {
  return {
    log_date: logDate,
    manual: {
      breakfast_log: nullableText(form.breakfastLog),
      lunch_log: nullableText(form.lunchLog),
      dinner_log: nullableText(form.dinnerLog),
      snacks_beverages_log: nullableText(form.snacksBeveragesLog),
      ate_from_outside: boolFromSelect(form.ateFromOutside),
      processed_food_consumed: boolFromSelect(form.processedFoodConsumed),
      unusual_food_exposure: boolFromSelect(form.unusualFoodExposure),
      unusual_exposure_notes: nullableText(form.unusualExposureNotes),
      energy_level: form.energyLevel ? (form.energyLevel as DailyLogPayload['manual']['energy_level']) : null,
      mood_today: form.moodToday ? (form.moodToday as DailyLogPayload['manual']['mood_today']) : null,
      overall_mental_feeling: form.overallMentalFeeling ? (form.overallMentalFeeling as DailyLogPayload['manual']['overall_mental_feeling']) : null,
      emotional_physical_impact: boolFromSelect(form.emotionalPhysicalImpact),
      physical_discomfort_notes: nullableText(form.physicalDiscomfortNotes),
      unusual_body_observation: nullableText(form.unusualBodyObservation),
      daily_events: splitList(form.dailyEvents),
      workload_intensity: form.workloadIntensity ? (form.workloadIntensity as DailyLogPayload['manual']['workload_intensity']) : null,
      crowded_place_exposure: boolFromSelect(form.crowdedPlaceExposure),
      travel_today: boolFromSelect(form.travelToday),
      emotional_event_notes: nullableText(form.emotionalEventNotes),
      chatbot_symptoms_reported: splitList(form.chatbotSymptomsReported),
      doctor_consulted_today: boolFromSelect(form.doctorConsultedToday),
      medical_visit_reason: nullableText(form.medicalVisitReason),
    },
  };
}

function numberText(row: Record<string, unknown>, key: string, unit = '') {
  const value = row[key];
  return typeof value === 'number' ? `${value}${unit}` : 'Auto-sync';
}

type FieldProps = {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
};

function TextField({ label, value, onChange, placeholder }: FieldProps) {
  return (
    <label className="space-y-2">
      <span className="block text-[11px] font-black uppercase text-on-surface-variant opacity-55">{label}</span>
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="h-12 w-full rounded-2xl border border-outline-variant/30 bg-white/90 px-4 text-sm font-semibold text-on-surface shadow-sm shadow-black/[0.02] outline-none transition-all duration-200 hover:border-primary/25 focus:border-primary focus:ring-4 focus:ring-primary/10"
      />
    </label>
  );
}

function TextAreaField({ label, value, onChange, placeholder }: FieldProps) {
  return (
    <label className="space-y-2 md:col-span-2">
      <span className="block text-[11px] font-black uppercase text-on-surface-variant opacity-55">{label}</span>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="min-h-28 w-full rounded-2xl border border-outline-variant/30 bg-white/90 p-4 text-sm font-semibold text-on-surface shadow-sm shadow-black/[0.02] outline-none transition-all duration-200 hover:border-primary/25 focus:border-primary focus:ring-4 focus:ring-primary/10"
      />
    </label>
  );
}

function SelectField({ label, value, onChange, options }: FieldProps & { options: string[] }) {
  return (
    <label className="space-y-2">
      <span className="block text-[11px] font-black uppercase text-on-surface-variant opacity-55">{label}</span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="h-12 w-full rounded-2xl border border-outline-variant/30 bg-white/90 px-4 text-sm font-semibold text-on-surface shadow-sm shadow-black/[0.02] outline-none transition-all duration-200 hover:border-primary/25 focus:border-primary focus:ring-4 focus:ring-primary/10"
      >
        <option value="">Not answered</option>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

function BooleanSelect({ label, value, onChange }: FieldProps) {
  return <SelectField label={label} value={value} onChange={onChange} options={['yes', 'no']} />;
}

function LogSection({ title, icon: Icon, children }: { title: string; icon: ElementType; children: ReactNode }) {
  return (
    <section className="premium-panel rounded-[2rem] p-6">
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary/10 text-primary">
          <Icon className="h-5 w-5" />
        </div>
        <h3 className="text-lg font-black text-on-surface">{title}</h3>
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">{children}</div>
    </section>
  );
}

export function DailyRoutineScreen() {
  const [selectedDay, setSelectedDay] = useState(6);
  const [form, setForm] = useState<FormState>(initialForm);
  const [dailyLog, setDailyLog] = useState<DailyLogResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [status, setStatus] = useState<'idle' | 'saved' | 'error'>('idle');
  const selectedDate = useMemo(() => dateForDay(selectedDay), [selectedDay]);

  const updateField = (field: keyof FormState, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
    setStatus('idle');
  };

  useEffect(() => {
    const controller = new AbortController();
    setIsLoading(true);
    setStatus('idle');

    fetchDailyLog(DEMO_USER_ID, selectedDate, controller.signal)
      .then((response) => {
        setDailyLog(response);
        setForm(formFromResponse(response));
      })
      .catch(() => {
        if (!controller.signal.aborted) {
          setDailyLog(null);
          setForm(initialForm);
          setStatus('error');
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      });

    return () => controller.abort();
  }, [selectedDate]);

  const handleSave = async () => {
    setIsSaving(true);
    setStatus('idle');
    try {
      const response = await saveDailyLog(DEMO_USER_ID, buildPayload(selectedDate, form));
      setDailyLog(response);
      setForm(formFromResponse(response));
      setStatus('saved');
    } catch {
      setStatus('error');
    } finally {
      setIsSaving(false);
    }
  };

  const fitness = dailyLog?.tables.daily_fitness_data ?? {};
  const environment = dailyLog?.tables.daily_environment_data ?? {};
  const device = dailyLog?.tables.daily_device_behavior_data ?? {};

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="mb-2 text-xs font-black uppercase text-primary">Manual daily questions</p>
          <h1 className="text-4xl font-black text-on-surface">Daily Routine</h1>
          <p className="mt-2 max-w-2xl text-sm font-semibold text-on-surface-variant opacity-70">
            Answer the date-wise questions. Fitness, device, environment, and calendar signals are generated automatically for this build.
          </p>
        </div>
        <button
          type="button"
          onClick={handleSave}
          disabled={isSaving || isLoading}
          className="inline-flex h-14 items-center justify-center gap-3 rounded-2xl bg-primary px-6 text-sm font-black text-white shadow-xl shadow-primary/20 transition-all duration-200 hover:bg-[#08513e] hover:shadow-2xl hover:shadow-primary/25 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSaving ? <Loader2 className="h-5 w-5 animate-spin" /> : <Save className="h-5 w-5" />}
          Save {selectedDate}
        </button>
      </div>

      <div className="grid grid-cols-1 gap-8 xl:grid-cols-[360px_1fr]">
        <aside className="space-y-6">
          <section className="premium-panel rounded-[2rem] p-6">
            <div className="mb-8 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-black text-on-surface">{monthLabel}</h2>
                <p className="mt-1 text-xs font-bold text-on-surface-variant opacity-60">Prediction training window</p>
              </div>
              <div className="flex gap-2">
                <button className="flex h-10 w-10 items-center justify-center rounded-2xl border border-outline-variant/30 text-on-surface-variant">
                  <ChevronLeft className="h-5 w-5" />
                </button>
                <button className="flex h-10 w-10 items-center justify-center rounded-2xl border border-outline-variant/30 text-on-surface-variant">
                  <ChevronRight className="h-5 w-5" />
                </button>
              </div>
            </div>

            <div className="grid grid-cols-7 text-center text-[10px] font-black uppercase text-on-surface-variant opacity-40">
              {days.map((day) => (
                <div key={day} className="pb-3">{day}</div>
              ))}
            </div>
            <div className="grid grid-cols-7 gap-2">
              {Array.from({ length: blankDaysBeforeMonth }).map((_, index) => <div key={`fill-${index}`} className="aspect-square" />)}
              {Array.from({ length: daysInMonth }).map((_, index) => {
                const day = index + 1;
                const isSelected = selectedDay === day;
                return (
                  <button
                    key={day}
                    type="button"
                    onClick={() => setSelectedDay(day)}
                    className={`aspect-square rounded-2xl text-sm font-black transition-all duration-200 active:scale-95 ${
                      isSelected ? 'bg-primary text-white shadow-xl shadow-primary/20' : 'bg-surface-container/60 text-on-surface hover:bg-primary/10 hover:text-primary'
                    }`}
                  >
                    {day}
                  </button>
                );
              })}
            </div>
          </section>

          <section className="rounded-[2rem] bg-zinc-950 p-6 text-white shadow-2xl shadow-black/20">
            <div className="mb-6 flex items-center gap-3">
              <CalendarDays className="h-5 w-5 text-[#aff0d6]" />
              <span className="text-xs font-black uppercase text-white/60">Selected date</span>
            </div>
            <p className="text-3xl font-black">{selectedDate}</p>
            <p className="mt-3 text-sm font-medium text-white/60">
              One save writes manual answers plus automatic daily signals into Supabase.
            </p>
            <AnimatePresence mode="wait">
              {status === 'saved' && (
                <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} className="mt-6 flex items-center gap-2 rounded-2xl bg-[#aff0d6]/15 px-4 py-3 text-sm font-black text-[#aff0d6]">
                  <CheckCircle className="h-4 w-4" />
                  Saved to prediction memory
                </motion.div>
              )}
              {status === 'error' && (
                <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} className="mt-6 flex items-center gap-2 rounded-2xl bg-rose-500/15 px-4 py-3 text-sm font-black text-rose-200">
                  <AlertTriangle className="h-4 w-4" />
                  Could not sync this log
                </motion.div>
              )}
            </AnimatePresence>
          </section>
        </aside>

        <div className="space-y-6">
          {isLoading && (
            <div className="flex items-center gap-3 rounded-2xl bg-white px-5 py-4 text-sm font-black text-on-surface-variant shadow-xl shadow-black/5">
              <Loader2 className="h-5 w-5 animate-spin text-primary" />
              Loading saved signals
            </div>
          )}

          <LogSection title="Food Intake" icon={Utensils}>
            <TextField label="What did you have for breakfast today?" value={form.breakfastLog} onChange={(value) => updateField('breakfastLog', value)} placeholder="oats, eggs, smoothie" />
            <TextField label="What did you have for lunch today?" value={form.lunchLog} onChange={(value) => updateField('lunchLog', value)} placeholder="rice bowl, salad" />
            <TextField label="What did you have for dinner today?" value={form.dinnerLog} onChange={(value) => updateField('dinnerLog', value)} placeholder="dal, noodles, soup" />
            <TextField label="Any snacks or beverages today?" value={form.snacksBeveragesLog} onChange={(value) => updateField('snacksBeveragesLog', value)} placeholder="coffee, chips, fruit" />
            <BooleanSelect label="Did you eat outside food today?" value={form.ateFromOutside} onChange={(value) => updateField('ateFromOutside', value)} />
            <BooleanSelect label="Did you consume processed/junk food today?" value={form.processedFoodConsumed} onChange={(value) => updateField('processedFoodConsumed', value)} />
            <BooleanSelect label="Any unusual food exposure today?" value={form.unusualFoodExposure} onChange={(value) => updateField('unusualFoodExposure', value)} />
            <TextAreaField label="Notes about unusual food exposure" value={form.unusualExposureNotes} onChange={(value) => updateField('unusualExposureNotes', value)} placeholder="new restaurant, spicy food, expired food, etc." />
          </LogSection>

          <LogSection title="Mood & Body" icon={Brain}>
            <SelectField label="How is your energy level today?" value={form.energyLevel} onChange={(value) => updateField('energyLevel', value)} options={energyOptions} />
            <SelectField label="How is your mood today?" value={form.moodToday} onChange={(value) => updateField('moodToday', value)} options={moodOptions} />
            <SelectField label="Overall emotional feeling today" value={form.overallMentalFeeling} onChange={(value) => updateField('overallMentalFeeling', value)} options={moodOptions} />
            <BooleanSelect label="Did emotions affect your body today?" value={form.emotionalPhysicalImpact} onChange={(value) => updateField('emotionalPhysicalImpact', value)} />
            <TextAreaField label="Any physical discomfort today?" value={form.physicalDiscomfortNotes} onChange={(value) => updateField('physicalDiscomfortNotes', value)} placeholder="headache, stomach discomfort, fatigue" />
            <TextAreaField label="Any unusual body observations?" value={form.unusualBodyObservation} onChange={(value) => updateField('unusualBodyObservation', value)} placeholder="skin, digestion, breathing, pain, etc." />
          </LogSection>

          <LogSection title="Events & Exposure" icon={Activity}>
            <TextField label="Important events today" value={form.dailyEvents} onChange={(value) => updateField('dailyEvents', value)} placeholder="comma separated" />
            <SelectField label="How intense was your workload today?" value={form.workloadIntensity} onChange={(value) => updateField('workloadIntensity', value)} options={workloadOptions} />
            <BooleanSelect label="Were you exposed to crowded places today?" value={form.crowdedPlaceExposure} onChange={(value) => updateField('crowdedPlaceExposure', value)} />
            <BooleanSelect label="Did you travel today?" value={form.travelToday} onChange={(value) => updateField('travelToday', value)} />
            <TextAreaField label="Any emotional event today?" value={form.emotionalEventNotes} onChange={(value) => updateField('emotionalEventNotes', value)} placeholder="argument, good news, pressure, grief, excitement" />
          </LogSection>

          <LogSection title="Chatbot & Medical Follow-up" icon={HeartPulse}>
            <TextField label="Symptoms reported to chatbot" value={form.chatbotSymptomsReported} onChange={(value) => updateField('chatbotSymptomsReported', value)} placeholder="comma separated" />
            <BooleanSelect label="Did you consult a doctor today?" value={form.doctorConsultedToday} onChange={(value) => updateField('doctorConsultedToday', value)} />
            <TextAreaField label="Reason for medical visit" value={form.medicalVisitReason} onChange={(value) => updateField('medicalVisitReason', value)} placeholder="routine checkup, fever, prescription, etc." />
          </LogSection>

          <section className="grid grid-cols-1 gap-4 md:grid-cols-4">
            {[
              { icon: Activity, label: 'Steps', value: numberText(fitness, 'steps') },
              { icon: HeartPulse, label: 'Sleep', value: numberText(fitness, 'sleep_duration_hours', 'h') },
              { icon: CloudSun, label: 'AQI', value: numberText(environment, 'aqi') },
              { icon: Smartphone, label: 'Screen', value: numberText(device, 'screen_time_hours', 'h') },
            ].map((item) => (
              <div key={item.label} className="rounded-[2rem] bg-white p-6 shadow-xl shadow-black/5">
                <item.icon className="mb-4 h-6 w-6 text-primary" />
                <p className="text-xs font-black uppercase text-on-surface-variant opacity-50">{item.label}</p>
                <p className="mt-2 text-xl font-black text-on-surface">{item.value}</p>
              </div>
            ))}
          </section>
        </div>
      </div>
    </motion.div>
  );
}
