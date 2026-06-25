import ZvZConsole from '@/components/ZvZConsole';

export const dynamic = 'force-dynamic';

export default function Participar() {
  return (
    <ZvZConsole apiBaseUrl={process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'} initialView="checkin" />
  );
}
