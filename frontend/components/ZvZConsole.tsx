'use client';

import type { FormEvent, ReactNode } from 'react';
import { useEffect, useMemo, useState } from 'react';

type View = 'staff' | 'eventBuilds' | 'eventManage' | 'builds' | 'leader' | 'checkin' | 'player' | 'settings';

type Player = {
  id: number;
  guild_id: number;
  albion_nick: string;
  rating: number;
  participations: number;
  role: string;
  is_staff: boolean;
  is_leader: boolean;
  active: boolean;
  discord_id?: string | null;
  discord_name?: string | null;
};

type AuthSession = {
  token: string;
  userId: number;
  nick: string;
  discordName: string;
};

type Event = {
  id: number;
  guild_id: number;
  title: string;
  content_type: string;
  event_date: string;
  status: string;
  created_by?: number | null;
  mount_gallop_requirement: number;
  mount_requirement_note?: string | null;
};

type Mount = {
  id: number;
  mount_name: string;
  display_name?: string | null;
  item_id?: string | null;
  icon_url?: string | null;
  tier?: string | null;
  move_speed_bonus?: number | null;
  gallop_speed_bonus?: number | null;
  max_load?: number | null;
  summary?: string | null;
  active: boolean;
};

type Build = {
  id: number;
  guild_id: number;
  name: string;
  build_type: string;
  role: string;
  weapon_name: string;
  weapon_item_id?: string | null;
  weapon_icon_url?: string | null;
  offhand?: string | null;
  offhand_item_id?: string | null;
  offhand_icon_url?: string | null;
  helmet?: string | null;
  helmet_item_id?: string | null;
  helmet_icon_url?: string | null;
  chest?: string | null;
  chest_item_id?: string | null;
  chest_icon_url?: string | null;
  boots?: string | null;
  boots_item_id?: string | null;
  boots_icon_url?: string | null;
  cape?: string | null;
  food?: string | null;
  potion?: string | null;
  recommended_mount?: string | null;
  required_level?: number | null;
  description?: string | null;
  active: boolean;
  allowed_mounts: string[];
  event_ids: number[];
  event_slots: BuildEventSlot[];
};

type BuildEventSlot = {
  event_id: number;
  max_slots: number;
  taken_slots: number;
  remaining_slots: number;
};

type Approval = {
  id: number;
  player_id: number;
  build_id: number;
  approved: boolean;
  build_name?: string | null;
  player_nick?: string | null;
};

type AlbionWeapon = {
  name: string;
  name_pt?: string | null;
  name_en?: string | null;
  item_id?: string | null;
  icon_url?: string | null;
  category?: string | null;
  tier?: string | number | null;
  variants?: AlbionWeaponVariant[];
};

type AlbionWeaponVariant = {
  tier?: string | null;
  item_id?: string | null;
  icon_url?: string | null;
  name?: string | null;
  name_en?: string | null;
};

type StaffDashboard = {
  total_players: number;
  total_events: number;
  total_checkins: number;
};

type Bucket = {
  label: string;
  total: number;
};

type Checkin = {
  id: number;
  event_id: number;
  user_id: number;
  build_id?: number | null;
  weapon_selected: string;
  mount_selected: string;
  checkin_time: string;
  approved: boolean;
  player_nick?: string | null;
  event_title?: string | null;
  build_name?: string | null;
  build_role?: string | null;
};

type BuildRequest = {
  id: number;
  guild_id: number;
  event_id: number;
  player_id: number;
  build_id: number;
  status: string;
  notes?: string | null;
  weapon_power?: number | null;
  leader_id?: number | null;
  created_at: string;
  decided_at?: string | null;
  event_title?: string | null;
  event_created_by?: number | null;
  player_nick?: string | null;
  build_name?: string | null;
  build_role?: string | null;
  build_icon_url?: string | null;
};

type Analytics = {
  total_participants: number;
  by_build: Bucket[];
  by_role: Bucket[];
  by_mount: Bucket[];
  by_content_type: Bucket[];
  top_builds: Bucket[];
  checkins: Checkin[];
};

type Notice = {
  tone: 'ok' | 'error' | 'info';
  text: string;
};

const emptyDashboard: StaffDashboard = {
  total_players: 0,
  total_events: 0,
  total_checkins: 0,
};

const emptyAnalytics: Analytics = {
  total_participants: 0,
  by_build: [],
  by_role: [],
  by_mount: [],
  by_content_type: [],
  top_builds: [],
  checkins: [],
};

const contentTypes = ['ZvZ', 'CTA', 'DG', 'Dungeon', 'Avalon', 'Gank', 'Defesa'];
const roles = ['Tank', 'DPS', 'Healer', 'Support', 'Debuff', 'Bomb Squad'];
const enchantments = ['0', '1', '2', '3', '4'];

function endpoint(apiBase: string, path: string) {
  return `${apiBase}${path}`;
}

async function request<T>(apiBase: string, path: string, init?: RequestInit): Promise<T> {
  let token = '';
  if (typeof window !== 'undefined') {
    const stored = window.localStorage.getItem('zvz_auth');
    if (stored) {
      try {
        token = String((JSON.parse(stored) as AuthSession).token ?? '');
      } catch {
        token = '';
      }
    }
  }

  const response = await fetch(endpoint(apiBase, path), {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    if (response.status === 401 && typeof window !== 'undefined') {
      window.localStorage.removeItem('zvz_auth');
      throw new Error('Sessao expirada ou invalida. Entre com Discord novamente para continuar.');
    }
    throw new Error(payload.detail ?? `Erro HTTP ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value));
}

function mountLabel(mount: Mount) {
  const name = mount.display_name || mount.mount_name;
  const tier = mount.tier ? ` T${mount.tier}` : '';
  return `${name}${tier}`;
}

function mountDetail(mount?: Mount | null) {
  if (!mount) return 'Montaria nao informada';
  const parts = [];
  if (mount.move_speed_bonus != null) parts.push(`${mount.move_speed_bonus}% velocidade`);
  if (mount.gallop_speed_bonus != null) parts.push(`${mount.gallop_speed_bonus}% galope`);
  if (mount.max_load != null) parts.push(`${mount.max_load}kg carga`);
  return parts.length ? parts.join(' / ') : mount.summary || mount.mount_name;
}

function slotLabel(slot?: BuildEventSlot | null) {
  if (!slot) return 'Vagas nao configuradas';
  return `${slot.taken_slots}/${slot.max_slots} preenchidas`;
}

function slotTone(slot?: BuildEventSlot | null) {
  if (!slot) return 'text-zinc-400';
  if (slot.remaining_slots <= 0) return 'text-red-300';
  if (slot.remaining_slots <= 1) return 'text-red-200';
  return 'text-emerald-300';
}

function isDungeonContent(value?: string | null) {
  return ['dg', 'dungeon', 'dungeons'].includes((value ?? '').trim().toLowerCase());
}

export default function ZvZConsole({
  apiBaseUrl,
  initialView = 'staff',
}: {
  apiBaseUrl: string;
  initialView?: View;
}) {
  const apiBase = apiBaseUrl.replace(/\/$/, '');
  const [view, setView] = useState<View>(initialView);
  const [players, setPlayers] = useState<Player[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [mounts, setMounts] = useState<Mount[]>([]);
  const [builds, setBuilds] = useState<Build[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [buildRequests, setBuildRequests] = useState<BuildRequest[]>([]);
  const [albionWeapons, setAlbionWeapons] = useState<AlbionWeapon[]>([]);
  const [albionArmors, setAlbionArmors] = useState<AlbionWeapon[]>([]);
  const [dashboard, setDashboard] = useState<StaffDashboard>(emptyDashboard);
  const [analytics, setAnalytics] = useState<Analytics>(emptyAnalytics);
  const [checkins, setCheckins] = useState<Checkin[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState<Notice>({ tone: 'info', text: 'Conectando com a API...' });
  const [authSession, setAuthSession] = useState<AuthSession | null>(null);

  const [playerForm, setPlayerForm] = useState({ albionNick: '' });
  const [eventForm, setEventForm] = useState({
    title: '',
    eventDate: '',
    status: 'open',
    contentType: 'ZvZ',
    mountGallopRequirement: '120',
    mountRequirementNote: '',
  });
  const [buildForm, setBuildForm] = useState({
    name: '',
    buildType: 'CTA',
    role: 'DPS',
    weaponBaseName: '',
    weaponName: '',
    weaponItemId: '',
    weaponIconUrl: '',
    weaponTier: '',
    weaponEnchant: '0',
    offhand: '',
    offhandBaseName: '',
    offhandItemId: '',
    offhandIconUrl: '',
    offhandTier: '',
    offhandEnchant: '0',
    helmet: '',
    helmetBaseName: '',
    helmetItemId: '',
    helmetIconUrl: '',
    helmetTier: '',
    helmetEnchant: '0',
    chest: '',
    chestBaseName: '',
    chestItemId: '',
    chestIconUrl: '',
    chestTier: '',
    chestEnchant: '0',
    boots: '',
    bootsBaseName: '',
    bootsItemId: '',
    bootsIconUrl: '',
    bootsTier: '',
    bootsEnchant: '0',
    cape: '',
    food: '',
    potion: '',
    recommendedMount: '',
    requiredLevel: '',
    description: '',
    mountNames: [] as string[],
  });
  const [checkinForm, setCheckinForm] = useState({ nick: '', eventId: '', buildId: '', mount: '' });
  const [requestWeaponPower, setRequestWeaponPower] = useState('');
  const [eventManageForm, setEventManageForm] = useState({ eventId: '', buildId: '', slots: '1' });
  const [eventEditForm, setEventEditForm] = useState({
    eventId: '',
    title: '',
    eventDate: '',
    status: 'open',
    contentType: 'ZvZ',
    mountGallopRequirement: '120',
    mountRequirementNote: '',
  });
  const [authNickForm, setAuthNickForm] = useState('');
  const [availableBuilds, setAvailableBuilds] = useState<Build[]>([]);
  const [filters, setFilters] = useState({ eventId: '', playerId: '', contentType: '', role: '', buildId: '' });

  const selectedCheckinBuild = useMemo(
    () => availableBuilds.find((build) => String(build.id) === checkinForm.buildId),
    [availableBuilds, checkinForm.buildId],
  );

  const selectedManagedEvent = useMemo(
    () => events.find((event) => String(event.id) === eventManageForm.eventId) ?? null,
    [eventManageForm.eventId, events],
  );

  const managedEventBuilds = useMemo(
    () =>
      selectedManagedEvent
        ? builds
            .map((build) => ({
              build,
              slot: build.event_slots.find((slot) => slot.event_id === selectedManagedEvent.id) ?? null,
            }))
            .filter((entry) => entry.slot)
        : [],
    [builds, selectedManagedEvent],
  );

  const managedEventCheckins = useMemo(
    () => checkins.filter((checkin) => String(checkin.event_id) === eventManageForm.eventId),
    [checkins, eventManageForm.eventId],
  );

  const managedEventPendingRequests = useMemo(
    () => buildRequests.filter((request) => String(request.event_id) === eventManageForm.eventId && request.status === 'pending'),
    [buildRequests, eventManageForm.eventId],
  );

  const managedEventCheckinsByBuild = useMemo(() => {
    const groups = new Map<string, Checkin[]>();
    managedEventCheckins.forEach((checkin) => {
      const key = checkin.build_name ?? checkin.weapon_selected ?? 'Sem build';
      groups.set(key, [...(groups.get(key) ?? []), checkin]);
    });
    return Array.from(groups.entries()).map(([buildName, rows]) => ({ buildName, rows }));
  }, [managedEventCheckins]);

  const managedEventConfirmed = useMemo(
    () => managedEventCheckins.filter((checkin) => checkin.approved).length,
    [managedEventCheckins],
  );

  const selectedCheckinEvent = useMemo(
    () => events.find((event) => String(event.id) === checkinForm.eventId) ?? null,
    [checkinForm.eventId, events],
  );

  const selectedCheckinEventIsDungeon = isDungeonContent(selectedCheckinEvent?.content_type);

  const selectedAlbionWeapon = useMemo(
    () => albionWeapons.find((item) => item.name === buildForm.weaponBaseName),
    [albionWeapons, buildForm.weaponBaseName],
  );

  const mountsByName = useMemo(() => {
    const map = new Map<string, Mount>();
    mounts.forEach((mount) => {
      map.set(mount.mount_name, mount);
      if (mount.display_name) map.set(mount.display_name, mount);
    });
    return map;
  }, [mounts]);

  const recommendedMount = useMemo(
    () => mountsByName.get(buildForm.recommendedMount) ?? null,
    [buildForm.recommendedMount, mountsByName],
  );

  const selectedCheckinMount = useMemo(
    () => mountsByName.get(checkinForm.mount) ?? null,
    [checkinForm.mount, mountsByName],
  );

  const checkinMountOptions = useMemo(() => {
    if (!selectedCheckinBuild) return [];
    const requiredGallop = selectedCheckinEvent?.mount_gallop_requirement ?? 120;
    return mounts
      .filter((mount) => (mount.gallop_speed_bonus ?? 0) >= requiredGallop)
      .map((mount) => mount.mount_name);
  }, [mounts, selectedCheckinBuild, selectedCheckinEvent]);

  const selectedCheckinSlot = useMemo(
    () => selectedCheckinBuild?.event_slots.find((slot) => String(slot.event_id) === checkinForm.eventId) ?? null,
    [checkinForm.eventId, selectedCheckinBuild],
  );

  const offhandOptions = useMemo(
    () => albionWeapons.filter((item) => item.variants?.some((variant) => variant.item_id?.includes('_OFF_') || variant.item_id?.startsWith('T4_OFF_'))),
    [albionWeapons],
  );
  const helmetOptions = useMemo(
    () => albionArmors.filter((item) => item.variants?.some((variant) => variant.item_id?.includes('_HEAD_'))),
    [albionArmors],
  );
  const chestOptions = useMemo(
    () => albionArmors.filter((item) => item.variants?.some((variant) => variant.item_id?.includes('_ARMOR_'))),
    [albionArmors],
  );
  const bootsOptions = useMemo(
    () => albionArmors.filter((item) => item.variants?.some((variant) => variant.item_id?.includes('_SHOES_'))),
    [albionArmors],
  );

  const ranking = useMemo(
    () =>
      [...players].sort((a, b) => {
        if (b.participations !== a.participations) return b.participations - a.participations;
        return b.rating - a.rating;
      }),
    [players],
  );

  const currentUser = useMemo(
    () => players.find((player) => player.id === authSession?.userId) ?? null,
    [authSession?.userId, players],
  );

  const canManage = Boolean(currentUser?.active && (currentUser.is_staff || currentUser.role === 'dev' || currentUser.role === 'staff'));
  const canLead = Boolean(currentUser?.active && (currentUser.is_leader || currentUser.is_staff || ['leader', 'staff', 'dev'].includes(currentUser.role)));
  const pendingBuildRequests = useMemo(
    () => buildRequests.filter((request) => {
      if (request.status !== 'pending') return false;
      if (canManage) return true;
      return request.event_created_by === currentUser?.id;
    }),
    [buildRequests, canManage, currentUser?.id],
  );

  useEffect(() => {
    if (!loading && !canManage && (view === 'staff' || view === 'eventBuilds' || view === 'eventManage' || view === 'builds' || view === 'settings')) {
      setView('checkin');
    }
    if (!loading && !canLead && view === 'leader') {
      setView('checkin');
    }
  }, [canLead, canManage, loading, view]);

  async function loadData() {
    setLoading(true);
    try {
      const [playersData, eventsData, mountsData, buildsData, approvalsData, checkinsData, dashboardData, analyticsData, albionData, armorData] =
        await Promise.all([
          request<Player[]>(apiBase, '/api/players/'),
          request<Event[]>(apiBase, '/api/events/'),
          request<Mount[]>(apiBase, '/api/mounts/'),
          request<Build[]>(apiBase, '/api/builds/'),
          request<Approval[]>(apiBase, '/api/builds/approvals'),
          request<Checkin[]>(apiBase, '/api/checkins/'),
          request<StaffDashboard>(apiBase, '/api/dashboard/staff'),
          request<Analytics>(apiBase, '/api/dashboard/analytics'),
          request<{ data: AlbionWeapon[] }>(apiBase, '/api/albion/weapons?limit=260&locale=pt-BR&grouped=true'),
          request<{ data: AlbionWeapon[] }>(apiBase, '/api/albion/weapons?limit=300&locale=pt-BR&grouped=true&item_type=armor'),
        ]);

      setPlayers(playersData);
      setEvents(eventsData);
      setMounts(mountsData);
      setBuilds(buildsData);
      setApprovals(approvalsData);
      setCheckins(checkinsData);
      setDashboard(dashboardData);
      setAnalytics(analyticsData);
      setAlbionWeapons(albionData.data);
      setAlbionArmors(armorData.data);
      setNotice((current) => (current.text === 'Conectando com a API...' ? { tone: 'info', text: '' } : current));
      if (window.localStorage.getItem('zvz_auth')) {
        try {
          const requestsData = await request<BuildRequest[]>(apiBase, '/api/build-requests/');
          setBuildRequests(requestsData);
        } catch {
          setBuildRequests([]);
        }
      } else {
        setBuildRequests([]);
      }
    } catch (error) {
      setNotice({
        tone: 'error',
        text: error instanceof Error ? error.message : 'Nao foi possivel carregar a API.',
      });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, [apiBase]);

  useEffect(() => {
    const stored = window.localStorage.getItem('zvz_auth');
    if (!stored) return;
    try {
      const parsed = JSON.parse(stored) as AuthSession;
      if (parsed.token && parsed.nick) {
        setAuthSession(parsed);
        setAuthNickForm(parsed.nick);
        setCheckinForm((current) => ({ ...current, nick: current.nick || parsed.nick }));
      }
    } catch {
      window.localStorage.removeItem('zvz_auth');
    }
  }, []);

  async function loginWithDiscord() {
    try {
      const payload = await request<{ url: string }>(apiBase, '/api/auth/discord/login');
      window.location.href = payload.url;
    } catch (error) {
      setNotice({
        tone: 'error',
        text: error instanceof Error ? error.message : 'Discord OAuth ainda nao esta configurado.',
      });
    }
  }

  function logout() {
    window.localStorage.removeItem('zvz_auth');
    setAuthSession(null);
    setNotice({ tone: 'ok', text: 'Sessao do Discord encerrada neste navegador.' });
  }

  async function saveAlbionNick() {
    if (!authSession || !authNickForm.trim()) {
      setNotice({ tone: 'error', text: 'Informe seu nick do Albion.' });
      return;
    }

    setSaving(true);
    try {
      const updated = await request<Player>(apiBase, `/api/players/${authSession.userId}`, {
        method: 'PUT',
        body: JSON.stringify({ albion_nick: authNickForm.trim() }),
      });
      const nextSession = { ...authSession, nick: updated.albion_nick };
      window.localStorage.setItem('zvz_auth', JSON.stringify(nextSession));
      setAuthSession(nextSession);
      setCheckinForm((current) => ({ ...current, nick: updated.albion_nick, buildId: '', mount: '' }));
      setNotice({ tone: 'ok', text: 'Nick do Albion atualizado para este login Discord.' });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha ao atualizar nick.' });
    } finally {
      setSaving(false);
    }
  }

  async function applyAnalyticsFilters(nextFilters = filters) {
    const params = new URLSearchParams();
    if (nextFilters.eventId) params.set('event_id', nextFilters.eventId);
    if (nextFilters.playerId) params.set('player_id', nextFilters.playerId);
    if (nextFilters.contentType) params.set('content_type', nextFilters.contentType);
    if (nextFilters.role) params.set('role', nextFilters.role);
    if (nextFilters.buildId) params.set('build_id', nextFilters.buildId);

    try {
      const suffix = params.toString() ? `?${params.toString()}` : '';
      const data = await request<Analytics>(apiBase, `/api/dashboard/analytics${suffix}`);
      setAnalytics(data);
      setNotice({ tone: 'ok', text: 'Analise atualizada com os filtros selecionados.' });
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha ao filtrar analise.' });
    }
  }

  useEffect(() => {
    async function loadAvailableBuilds() {
      if (selectedCheckinEventIsDungeon) {
        setAvailableBuilds(
          builds.filter((build) =>
            build.active &&
            build.event_slots.some((slot) => String(slot.event_id) === checkinForm.eventId && slot.remaining_slots > 0),
          ),
        );
        return;
      }

      if (!checkinForm.nick.trim() || !checkinForm.eventId) {
        setAvailableBuilds([]);
        return;
      }

      try {
        const payload = await request<{ builds: Build[] }>(
          apiBase,
          `/api/builds/available?nick=${encodeURIComponent(checkinForm.nick)}&event_id=${checkinForm.eventId}`,
        );
        setAvailableBuilds(payload.builds);
      } catch {
        setAvailableBuilds([]);
      }
    }

    void loadAvailableBuilds();
  }, [apiBase, builds, checkinForm.nick, checkinForm.eventId, selectedCheckinEventIsDungeon]);

  function weaponIconUrl(itemId: string, enchant: string) {
    return `https://render.albiononline.com/v1/item/${itemId}@${enchant}.png?quality=0&size=217&locale=pt-BR`;
  }

  function chooseAlbionWeapon(name: string) {
    const weapon = albionWeapons.find((item) => item.name === name);
    const variant = weapon?.variants?.[0];
    const enchant = '0';
    setBuildForm({
      ...buildForm,
      weaponBaseName: name,
      weaponName: variant?.tier ? `${name} T${variant.tier}` : name,
      weaponItemId: variant?.item_id ? `${variant.item_id}@${enchant}` : '',
      weaponIconUrl: variant?.item_id ? weaponIconUrl(variant.item_id, enchant) : '',
      weaponTier: variant?.tier ?? '',
      weaponEnchant: enchant,
    });
  }

  function chooseWeaponVariant(tier: string, enchant = buildForm.weaponEnchant) {
    const variant = selectedAlbionWeapon?.variants?.find((item) => item.tier === tier);
    setBuildForm({
      ...buildForm,
      weaponName: tier ? `${buildForm.weaponBaseName} T${tier}${enchant !== '0' ? `.${enchant}` : ''}` : buildForm.weaponBaseName,
      weaponItemId: variant?.item_id ? `${variant.item_id}@${enchant}` : '',
      weaponIconUrl: variant?.item_id ? weaponIconUrl(variant.item_id, enchant) : '',
      weaponTier: tier,
      weaponEnchant: enchant,
    });
  }

  type GearSlot = 'offhand' | 'helmet' | 'chest' | 'boots';

  function slotFields(slot: GearSlot) {
    return {
      base: `${slot}BaseName`,
      name: slot,
      itemId: `${slot}ItemId`,
      iconUrl: `${slot}IconUrl`,
      tier: `${slot}Tier`,
      enchant: `${slot}Enchant`,
    } as const;
  }

  function chooseGearItem(slot: GearSlot, options: AlbionWeapon[], name: string) {
    const item = options.find((option) => option.name === name);
    const variant = item?.variants?.[0];
    const enchant = '0';
    const fields = slotFields(slot);
    setBuildForm({
      ...buildForm,
      [fields.base]: name,
      [fields.name]: variant?.tier ? `${name} T${variant.tier}` : name,
      [fields.itemId]: variant?.item_id ? `${variant.item_id}@${enchant}` : '',
      [fields.iconUrl]: variant?.item_id ? weaponIconUrl(variant.item_id, enchant) : '',
      [fields.tier]: variant?.tier ?? '',
      [fields.enchant]: enchant,
    });
  }

  function chooseGearVariant(slot: GearSlot, options: AlbionWeapon[], tier: string, enchant: string) {
    const fields = slotFields(slot);
    const baseName = String(buildForm[fields.base as keyof typeof buildForm] ?? '');
    const item = options.find((option) => option.name === baseName);
    const variant = item?.variants?.find((entry) => entry.tier === tier);
    setBuildForm({
      ...buildForm,
      [fields.name]: tier ? `${baseName} T${tier}${enchant !== '0' ? `.${enchant}` : ''}` : baseName,
      [fields.itemId]: variant?.item_id ? `${variant.item_id}@${enchant}` : '',
      [fields.iconUrl]: variant?.item_id ? weaponIconUrl(variant.item_id, enchant) : '',
      [fields.tier]: tier,
      [fields.enchant]: enchant,
    });
  }

  async function createPlayer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    try {
      await request<Player>(apiBase, '/api/players/', {
        method: 'POST',
        body: JSON.stringify({
          guild_id: 1,
          albion_nick: playerForm.albionNick,
          discord_id: playerForm.albionNick.trim().toLowerCase(),
          discord_name: playerForm.albionNick,
        }),
      });
      setPlayerForm({ albionNick: '' });
      setNotice({ tone: 'ok', text: 'Jogador cadastrado. Libere builds para ele na aba Builds.' });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha no cadastro.' });
    } finally {
      setSaving(false);
    }
  }

  async function createEvent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    try {
      await request<Event>(apiBase, '/api/events/', {
        method: 'POST',
        body: JSON.stringify({
          guild_id: 1,
          title: eventForm.title,
          content_type: eventForm.contentType,
          event_date: new Date(eventForm.eventDate).toISOString(),
          status: eventForm.status,
          mount_gallop_requirement: Number(eventForm.mountGallopRequirement || 120),
          mount_requirement_note: eventForm.mountRequirementNote || null,
        }),
      });
      setEventForm({
        title: '',
        eventDate: '',
        status: 'open',
        contentType: 'ZvZ',
        mountGallopRequirement: '120',
        mountRequirementNote: '',
      });
      setNotice({ tone: 'ok', text: 'Evento criado. Selecione as builds e vagas no gerenciador do evento.' });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha ao criar evento.' });
    } finally {
      setSaving(false);
    }
  }

  async function duplicateEvent(source: Event) {
    setSaving(true);
    try {
      const duplicated = await request<Event>(apiBase, `/api/events/${source.id}/duplicate`, {
        method: 'POST',
        body: JSON.stringify({
          title: `Base - ${source.title}`,
          status: 'draft',
        }),
      });
      setEventManageForm({ eventId: String(duplicated.id), buildId: '', slots: '1' });
      setView('eventBuilds');
      setNotice({ tone: 'ok', text: `Evento base criado com a composicao de ${source.title}.` });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha ao duplicar evento.' });
    } finally {
      setSaving(false);
    }
  }

  async function setEventStatus(event: Event, status: 'open' | 'closed') {
    setSaving(true);
    try {
      await request<Event>(apiBase, `/api/events/${event.id}/${status === 'closed' ? 'close' : 'reopen'}`, { method: 'POST' });
      setNotice({ tone: 'ok', text: status === 'closed' ? `Evento ${event.title} fechado.` : `Evento ${event.title} reaberto.` });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha ao alterar status do evento.' });
    } finally {
      setSaving(false);
    }
  }

  function startEventEdit(event: Event) {
    setEventEditForm({
      eventId: String(event.id),
      title: event.title,
      eventDate: event.event_date.slice(0, 16),
      status: event.status,
      contentType: event.content_type,
      mountGallopRequirement: String(event.mount_gallop_requirement ?? 120),
      mountRequirementNote: event.mount_requirement_note ?? '',
    });
  }

  async function saveEventEdit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!eventEditForm.eventId) return;
    setSaving(true);
    try {
      await request<Event>(apiBase, `/api/events/${eventEditForm.eventId}`, {
        method: 'PUT',
        body: JSON.stringify({
          title: eventEditForm.title,
          content_type: eventEditForm.contentType,
          event_date: new Date(eventEditForm.eventDate).toISOString(),
          status: eventEditForm.status,
          mount_gallop_requirement: Number(eventEditForm.mountGallopRequirement || 120),
          mount_requirement_note: eventEditForm.mountRequirementNote || null,
        }),
      });
      setEventEditForm({
        eventId: '',
        title: '',
        eventDate: '',
        status: 'open',
        contentType: 'ZvZ',
        mountGallopRequirement: '120',
        mountRequirementNote: '',
      });
      setNotice({ tone: 'ok', text: 'Evento atualizado.' });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha ao editar evento.' });
    } finally {
      setSaving(false);
    }
  }

  async function createBuild(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    try {
      await request<Build>(apiBase, '/api/builds/', {
        method: 'POST',
        body: JSON.stringify({
          guild_id: 1,
          name: buildForm.name,
          build_type: buildForm.buildType,
          role: buildForm.role,
          weapon_name: buildForm.weaponName,
          weapon_item_id: buildForm.weaponItemId || null,
          weapon_icon_url: buildForm.weaponIconUrl || null,
          offhand: buildForm.offhand || null,
          offhand_item_id: buildForm.offhandItemId || null,
          offhand_icon_url: buildForm.offhandIconUrl || null,
          helmet: buildForm.helmet || null,
          helmet_item_id: buildForm.helmetItemId || null,
          helmet_icon_url: buildForm.helmetIconUrl || null,
          chest: buildForm.chest || null,
          chest_item_id: buildForm.chestItemId || null,
          chest_icon_url: buildForm.chestIconUrl || null,
          boots: buildForm.boots || null,
          boots_item_id: buildForm.bootsItemId || null,
          boots_icon_url: buildForm.bootsIconUrl || null,
          cape: buildForm.cape || null,
          food: buildForm.food || null,
          potion: buildForm.potion || null,
          recommended_mount: buildForm.recommendedMount || null,
          required_level: buildForm.requiredLevel ? Number(buildForm.requiredLevel) : null,
          description: buildForm.description || null,
          allowed_mounts: [],
          event_slots: [],
          active: true,
        }),
      });
      setBuildForm({
        name: '',
        buildType: 'CTA',
        role: 'DPS',
        weaponBaseName: '',
        weaponName: '',
        weaponItemId: '',
        weaponIconUrl: '',
        weaponTier: '',
        weaponEnchant: '0',
        offhand: '',
        offhandBaseName: '',
        offhandItemId: '',
        offhandIconUrl: '',
        offhandTier: '',
        offhandEnchant: '0',
        helmet: '',
        helmetBaseName: '',
        helmetItemId: '',
        helmetIconUrl: '',
        helmetTier: '',
        helmetEnchant: '0',
        chest: '',
        chestBaseName: '',
        chestItemId: '',
        chestIconUrl: '',
        chestTier: '',
        chestEnchant: '0',
        boots: '',
        bootsBaseName: '',
        bootsItemId: '',
        bootsIconUrl: '',
        bootsTier: '',
        bootsEnchant: '0',
        cape: '',
        food: '',
        potion: '',
        recommendedMount: '',
        requiredLevel: '',
        description: '',
        mountNames: [],
      });
      setNotice({ tone: 'ok', text: 'Build criada. Agora libere jogadores aqui ou use em eventos pela aba Eventos.' });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha ao criar build.' });
    } finally {
      setSaving(false);
    }
  }

  async function toggleApproval(player: Player, build: Build) {
    const current = approvals.find((approval) => approval.player_id === player.id && approval.build_id === build.id);
    setSaving(true);
    try {
      await request<Approval>(apiBase, '/api/builds/approvals', {
        method: 'POST',
        body: JSON.stringify({
          guild_id: player.guild_id,
          player_id: player.id,
          build_id: build.id,
          approved: !current?.approved,
        }),
      });
      setNotice({ tone: 'ok', text: `Build ${build.name} atualizada para ${player.albion_nick}.` });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha ao aprovar build.' });
    } finally {
      setSaving(false);
    }
  }

  async function deactivateBuild(build: Build) {
    setSaving(true);
    try {
      await request<Build>(apiBase, `/api/builds/${build.id}`, { method: 'DELETE' });
      setNotice({ tone: 'ok', text: `Build ${build.name} foi inativada.` });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha ao inativar build.' });
    } finally {
      setSaving(false);
    }
  }

  async function reactivateBuild(build: Build) {
    setSaving(true);
    try {
      await request<Build>(apiBase, `/api/builds/${build.id}/reactivate`, { method: 'POST' });
      setNotice({ tone: 'ok', text: `Build ${build.name} foi reativada.` });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha ao reativar build.' });
    } finally {
      setSaving(false);
    }
  }

  async function updatePlayerAccess(player: Player, next: Partial<Pick<Player, 'role' | 'is_staff' | 'is_leader' | 'active'>>) {
    setSaving(true);
    try {
      await request<Player>(apiBase, `/api/players/${player.id}`, {
        method: 'PUT',
        body: JSON.stringify(next),
      });
      setNotice({ tone: 'ok', text: `Acesso de ${player.albion_nick} atualizado.` });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha ao atualizar jogador.' });
    } finally {
      setSaving(false);
    }
  }

  async function deactivatePlayer(player: Player) {
    setSaving(true);
    try {
      await request<Player>(apiBase, `/api/players/${player.id}`, { method: 'DELETE' });
      setNotice({ tone: 'ok', text: `${player.albion_nick} foi inativado. O historico e ranking foram preservados.` });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha ao inativar jogador.' });
    } finally {
      setSaving(false);
    }
  }

  async function reactivatePlayer(player: Player) {
    setSaving(true);
    try {
      await request<Player>(apiBase, `/api/players/${player.id}/reactivate`, { method: 'POST' });
      setNotice({ tone: 'ok', text: `${player.albion_nick} foi reativado.` });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha ao reativar jogador.' });
    } finally {
      setSaving(false);
    }
  }

  async function updateBuildEventSlots(build: Build, eventSlots: { event_id: number; max_slots: number }[], message: string) {
    setSaving(true);
    try {
      await request<Build>(apiBase, `/api/builds/${build.id}`, {
        method: 'PUT',
        body: JSON.stringify({
          event_slots: eventSlots,
          allowed_mounts: [],
        }),
      });
      setNotice({ tone: 'ok', text: message });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha ao atualizar evento da build.' });
    } finally {
      setSaving(false);
    }
  }

  async function linkBuildToManagedEvent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const managedEventId = Number(eventManageForm.eventId);
    const build = builds.find((item) => String(item.id) === eventManageForm.buildId);
    if (!managedEventId || !build) {
      setNotice({ tone: 'error', text: 'Selecione o evento e a build para vincular.' });
      return;
    }

    const slots = Math.max(Number(eventManageForm.slots || 1), 1);
    const nextSlots = build.event_slots
      .filter((slot) => slot.event_id !== managedEventId)
      .map((slot) => ({ event_id: slot.event_id, max_slots: slot.max_slots }));
    nextSlots.push({ event_id: managedEventId, max_slots: slots });

    await updateBuildEventSlots(build, nextSlots, `Build ${build.name} vinculada ao evento com ${slots} vaga(s).`);
    setEventManageForm((current) => ({ ...current, buildId: '', slots: '1' }));
  }

  async function changeManagedBuildSlots(build: Build, eventId: number, slots: number) {
    const nextSlots = build.event_slots.map((slot) => ({
      event_id: slot.event_id,
      max_slots: slot.event_id === eventId ? Math.max(slots, 1) : slot.max_slots,
    }));
    await updateBuildEventSlots(build, nextSlots, `Vagas de ${build.name} atualizadas.`);
  }

  async function unlinkBuildFromManagedEvent(build: Build, eventId: number) {
    const nextSlots = build.event_slots
      .filter((slot) => slot.event_id !== eventId)
      .map((slot) => ({ event_id: slot.event_id, max_slots: slot.max_slots }));
    await updateBuildEventSlots(build, nextSlots, `Build ${build.name} removida do evento.`);
  }

  async function toggleCheckinStatus(checkin: Checkin) {
    setSaving(true);
    try {
      await request<Checkin>(apiBase, `/api/checkins/${checkin.id}`, {
        method: 'PUT',
        body: JSON.stringify({ approved: !checkin.approved }),
      });
      setNotice({ tone: 'ok', text: `Check-in de ${checkin.player_nick ?? checkin.user_id} atualizado.` });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha ao atualizar check-in.' });
    } finally {
      setSaving(false);
    }
  }

  async function removeCheckinFromEvent(checkin: Checkin) {
    setSaving(true);
    try {
      await request(apiBase, `/api/checkins/${checkin.id}`, { method: 'DELETE' });
      setNotice({ tone: 'ok', text: `${checkin.player_nick ?? checkin.user_id} removido do grupo do evento.` });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha ao remover check-in.' });
    } finally {
      setSaving(false);
    }
  }

  async function requestDungeonBuild(build: Build) {
    if (!authSession) {
      setNotice({ tone: 'error', text: 'Entre com Discord para solicitar build em DG.' });
      return;
    }
    if (!selectedCheckinEvent) {
      setNotice({ tone: 'error', text: 'Selecione uma DG antes de solicitar a build.' });
      return;
    }

    const parsedWeaponPower = requestWeaponPower.trim() ? Number(requestWeaponPower) : null;
    if (requestWeaponPower.trim() && Number.isNaN(parsedWeaponPower)) {
      setNotice({ tone: 'error', text: 'Informe um valor numerico valido para o IP da arma.' });
      return;
    }

    setSaving(true);
    try {
      await request<BuildRequest>(apiBase, '/api/build-requests/', {
        method: 'POST',
        body: JSON.stringify({
          event_id: selectedCheckinEvent.id,
          build_id: build.id,
          weapon_power: parsedWeaponPower,
        }),
      });
      setRequestWeaponPower('');
      setNotice({ tone: 'ok', text: `Solicitacao enviada aos lideres para usar ${build.name}.` });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha ao solicitar build.' });
    } finally {
      setSaving(false);
    }
  }

  async function decideBuildRequest(buildRequest: BuildRequest, status: 'approved' | 'rejected') {
    setSaving(true);
    try {
      await request<BuildRequest>(apiBase, `/api/build-requests/${buildRequest.id}`, {
        method: 'PUT',
        body: JSON.stringify({ status }),
      });
      setNotice({
        tone: 'ok',
        text: status === 'approved'
          ? `${buildRequest.player_nick ?? 'Player'} aprovado para ${buildRequest.build_name ?? 'build'}.`
          : `${buildRequest.player_nick ?? 'Player'} rejeitado para ${buildRequest.build_name ?? 'build'}.`,
      });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha ao decidir solicitacao.' });
    } finally {
      setSaving(false);
    }
  }

  async function submitCheckin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const build = selectedCheckinBuild;
    if (!build) {
      setNotice({ tone: 'error', text: 'Selecione uma build liberada para este nick e evento.' });
      return;
    }

    const player = players.find((item) => item.albion_nick.trim().toLowerCase() === checkinForm.nick.trim().toLowerCase());
    if (!player) {
      setNotice({ tone: 'error', text: 'Nick nao encontrado no cadastro.' });
      return;
    }

    setSaving(true);
    try {
      await request(apiBase, '/api/checkins/', {
        method: 'POST',
        body: JSON.stringify({
          guild_id: player.guild_id,
          event_id: Number(checkinForm.eventId),
          user_id: player.id,
          build_id: build.id,
          weapon_selected: build.name,
          mount_selected: checkinForm.mount,
          approved: true,
        }),
      });
      setCheckinForm({ nick: '', eventId: '', buildId: '', mount: '' });
      setAvailableBuilds([]);
      setNotice({ tone: 'ok', text: 'Check-in registrado com build autorizada.' });
      await loadData();
    } catch (error) {
      setNotice({ tone: 'error', text: error instanceof Error ? error.message : 'Falha no check-in.' });
    } finally {
      setSaving(false);
    }
  }

  const noticeClass =
    notice.tone === 'ok'
      ? 'border-emerald-400/40 bg-emerald-400/10 text-emerald-100'
      : notice.tone === 'error'
        ? 'border-red-400/40 bg-red-400/10 text-red-100'
        : 'border-zinc-600 bg-zinc-800 text-zinc-200';

  function gearValue(field: string) {
    return String((buildForm as Record<string, unknown>)[field] ?? '');
  }

  function gearSelector(slot: GearSlot, label: string, options: AlbionWeapon[]) {
    const fields = slotFields(slot);
    const baseName = gearValue(fields.base);
    const selected = options.find((item) => item.name === baseName);
    const tier = gearValue(fields.tier);
    const enchant = gearValue(fields.enchant) || '0';
    const icon = gearValue(fields.iconUrl);
    const name = gearValue(fields.name);

    return (
      <div className="rounded border border-zinc-800 bg-zinc-950 p-3">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">{label}</p>
        <div className="grid gap-2 md:grid-cols-[1.4fr_0.7fr_0.7fr]">
          <select className="control" onChange={(event) => chooseGearItem(slot, options, event.target.value)} value={baseName}>
            <option value="">Item</option>
            {options.map((item) => <option key={item.name_en ?? item.name} value={item.name}>{item.name}</option>)}
          </select>
          <select className="control" disabled={!selected} onChange={(event) => chooseGearVariant(slot, options, event.target.value, enchant)} value={tier}>
            <option value="">Tier</option>
            {(selected?.variants ?? []).map((variant) => (
              <option key={`${variant.item_id}-${variant.tier}`} value={variant.tier ?? ''}>T{variant.tier}</option>
            ))}
          </select>
          <select className="control" disabled={!selected} onChange={(event) => chooseGearVariant(slot, options, tier, event.target.value)} value={enchant}>
            {enchantments.map((item) => <option key={item} value={item}>{item === '0' ? 'Sem encanto' : `.${item}`}</option>)}
          </select>
        </div>
        {icon ? (
          <div className="mt-3 flex items-center gap-3">
            <img alt="" className="h-12 w-12 rounded bg-zinc-900 object-contain" src={icon} />
            <span className="text-sm text-zinc-300">{name}</span>
          </div>
        ) : null}
      </div>
    );
  }

  const navItems = (canManage
    ? ['staff', 'eventBuilds', 'eventManage', 'builds', 'leader', 'checkin', 'player', 'settings']
    : canLead
      ? ['leader', 'checkin', 'player']
      : ['checkin', 'player']) as View[];
  const viewLabels: Record<View, string> = {
    staff: 'Eventos',
    eventBuilds: 'Composicao',
    eventManage: 'Gerenciar',
    builds: 'Builds',
    leader: 'Lider',
    checkin: 'Check-in',
    player: 'Jogador',
    settings: 'Configuracoes',
  };

  return (
    <main className="app-shell min-h-screen text-zinc-100">
      <aside className="app-sidebar">
        <div className="brand-block">
          <div className="brand-mark" aria-hidden="true">
            <span className="brand-mark-core">
              <span />
            </span>
          </div>
          <div className="brand-copy">
            <p className="brand-title">Nam3less</p>
            <p className="brand-subtitle">ZvZ Management System</p>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <button
              key={item}
              className={`sidebar-link ${view === item ? 'sidebar-link-active' : ''}`}
              onClick={() => setView(item)}
              type="button"
            >
              {viewLabels[item]}
            </button>
          ))}
        </nav>

        <div className="sidebar-user">
          <div className="user-avatar">
            <span />
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-zinc-100">{authSession?.discordName ?? 'Visitante'}</p>
            <p className="truncate text-xs text-zinc-500">{canManage ? 'Shotcaller / Staff' : authSession ? 'Membro' : 'Discord desconectado'}</p>
          </div>
        </div>
      </aside>

      <section className="app-main">
        <header className="app-header">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-red-400">Albion Online ZvZ</p>
            <h1 className="mt-2 text-2xl font-bold text-white sm:text-3xl">Painel Operacional ZvZ</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-400">
              Controle tatico de eventos, builds, check-ins, staff e historico da guilda.
            </p>
          </div>

          <div className="header-ops">
            <div className="hidden gap-6 lg:flex">
              <Metric label="Jogadores" value={dashboard.total_players} compact />
              <Metric label="Eventos" value={dashboard.total_events} compact />
              <Metric label="Check-ins" value={dashboard.total_checkins} compact />
            </div>
            <div className="flex min-h-10 flex-wrap items-center justify-end gap-2">
              {authSession ? (
                <>
                  <span className="rounded border border-emerald-400/30 bg-emerald-400/10 px-3 py-2 text-xs font-semibold text-emerald-100">
                    Discord: {authSession.discordName}{canManage ? ' / staff' : ''}
                  </span>
                  <button className="button-secondary h-10" onClick={logout} type="button">Sair</button>
                </>
              ) : (
                <button className="button-primary h-10" onClick={() => void loginWithDiscord()} type="button">
                  Entrar com Discord
                </button>
              )}
            </div>
          </div>
        </header>

        {(loading || notice.text) ? (
          <div className={`rounded-md border px-4 py-3 text-sm ${noticeClass}`}>
            {loading ? 'Carregando dados...' : notice.text}
          </div>
        ) : null}

        {authSession ? (
          <section className="surface rounded-md p-4">
            <div className="grid gap-3 md:grid-cols-[1fr_auto] md:items-end">
              <label className="grid gap-2 text-sm">
                <span className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Nick Albion vinculado ao Discord</span>
                <input
                  className="control"
                  onChange={(event) => setAuthNickForm(event.target.value)}
                  placeholder="Seu nick no Albion"
                  value={authNickForm}
                />
              </label>
              <button className="button-primary" disabled={saving || !authNickForm.trim()} onClick={() => void saveAlbionNick()} type="button">
                Salvar nick Albion
              </button>
            </div>
            <p className="mt-2 text-xs text-zinc-500">
              Alterar este nick afeta proximos check-ins e liberacoes futuras. Relatorios antigos mantem o nick registrado no momento do check-in.
            </p>
          </section>
        ) : null}

        {view === 'staff' && canManage ? (
          <section className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
            <div className="space-y-5">
              <div className="grid gap-3 sm:grid-cols-4">
                <Metric label="Jogadores" value={dashboard.total_players} />
                <Metric label="Eventos" value={dashboard.total_events} />
                <Metric label="Check-ins" value={dashboard.total_checkins} />
                <Metric label="Builds" value={builds.length} />
              </div>
              <Panel title="Analise por filtros">
                <div className="grid gap-3 md:grid-cols-5">
                  <select className="control" onChange={(event) => setFilters({ ...filters, eventId: event.target.value })} value={filters.eventId}>
                    <option value="">Evento</option>
                    {events.map((event) => <option key={event.id} value={event.id}>{event.title}</option>)}
                  </select>
                  <select className="control" onChange={(event) => setFilters({ ...filters, playerId: event.target.value })} value={filters.playerId}>
                    <option value="">Player</option>
                    {players.map((player) => <option key={player.id} value={player.id}>{player.albion_nick}</option>)}
                  </select>
                  <select className="control" onChange={(event) => setFilters({ ...filters, contentType: event.target.value })} value={filters.contentType}>
                    <option value="">Conteudo</option>
                    {contentTypes.map((item) => <option key={item} value={item}>{item}</option>)}
                  </select>
                  <select className="control" onChange={(event) => setFilters({ ...filters, role: event.target.value })} value={filters.role}>
                    <option value="">Funcao</option>
                    {roles.map((item) => <option key={item} value={item}>{item}</option>)}
                  </select>
                  <select className="control" onChange={(event) => setFilters({ ...filters, buildId: event.target.value })} value={filters.buildId}>
                    <option value="">Build</option>
                    {builds.map((build) => <option key={build.id} value={build.id}>{build.name}</option>)}
                  </select>
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  <button className="button-primary" type="button" onClick={() => void applyAnalyticsFilters()}>Aplicar filtros</button>
                  <button className="button-secondary" type="button" onClick={() => { const clean = { eventId: '', playerId: '', contentType: '', role: '', buildId: '' }; setFilters(clean); void applyAnalyticsFilters(clean); }}>Limpar</button>
                </div>
                <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                  <Metric label="Participantes filtrados" value={analytics.total_participants} />
                  <BucketList title="Por build" rows={analytics.by_build} />
                  <BucketList title="Por funcao" rows={analytics.by_role} />
                  <BucketList title="Montarias" rows={analytics.by_mount} />
                </div>
              </Panel>
              <Panel title="Jogadores">
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[640px] border-collapse text-sm">
                    <thead>
                      <tr className="border-b border-zinc-800 text-left text-xs uppercase text-zinc-500">
                        <th className="py-3">Nick</th>
                        <th>Nota</th>
                        <th>Presencas</th>
                        <th>Builds liberadas</th>
                      </tr>
                    </thead>
                    <tbody>
                      {players.map((player) => (
                        <tr key={player.id} className="border-b border-zinc-800/70">
                          <td className="py-3 font-semibold text-zinc-100">{player.albion_nick}</td>
                          <td>{player.rating.toFixed(1)}</td>
                          <td>{player.participations}</td>
                          <td>{approvals.filter((approval) => approval.player_id === player.id && approval.approved).length}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Panel>
              <Panel title="Participantes e check-ins">
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[860px] border-collapse text-sm">
                    <thead>
                      <tr className="border-b border-zinc-800 text-left text-xs uppercase text-zinc-500">
                        <th className="py-3">Jogador</th>
                        <th>Evento</th>
                        <th>Build</th>
                        <th>Funcao</th>
                        <th>Montaria</th>
                        <th>Check-in</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analytics.checkins.map((checkin) => (
                        <tr key={checkin.id} className="border-b border-zinc-800/70">
                          <td className="py-3 font-semibold text-zinc-100">{checkin.player_nick ?? checkin.user_id}</td>
                          <td>{checkin.event_title ?? checkin.event_id}</td>
                          <td>{checkin.build_name ?? checkin.weapon_selected}</td>
                          <td>{checkin.build_role ?? 'Nao informado'}</td>
                          <td>{mountsByName.get(checkin.mount_selected)?.display_name || checkin.mount_selected}</td>
                          <td>{formatDate(checkin.checkin_time)}</td>
                          <td>{checkin.approved ? 'Confirmado' : 'Pendente'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Panel>
            </div>

            <div className="space-y-5">
              <Panel title="Novo evento">
                <form className="grid gap-3" onSubmit={createEvent}>
                  <input className="control" onChange={(event) => setEventForm({ ...eventForm, title: event.target.value })} placeholder="CTA 21h - Martlock" required value={eventForm.title} />
                  <input className="control" onChange={(event) => setEventForm({ ...eventForm, eventDate: event.target.value })} required type="datetime-local" value={eventForm.eventDate} />
                  <select className="control" onChange={(event) => setEventForm({ ...eventForm, contentType: event.target.value })} value={eventForm.contentType}>
                    {contentTypes.map((item) => <option key={item} value={item}>{item}</option>)}
                  </select>
                  <select className="control" onChange={(event) => setEventForm({ ...eventForm, status: event.target.value })} value={eventForm.status}>
                    <option value="open">Aberto</option>
                    <option value="draft">Rascunho</option>
                    <option value="closed">Fechado</option>
                  </select>
                  <input
                    className="control"
                    min={0}
                    onChange={(event) => setEventForm({ ...eventForm, mountGallopRequirement: event.target.value })}
                    placeholder="Galope minimo"
                    type="number"
                    value={eventForm.mountGallopRequirement}
                  />
                  <textarea
                    className="control min-h-20 py-3"
                    onChange={(event) => setEventForm({ ...eventForm, mountRequirementNote: event.target.value })}
                    placeholder="Texto da regra de montaria. Ex: apenas cavalo gigante."
                    value={eventForm.mountRequirementNote}
                  />
                  <button className="button-primary" disabled={saving} type="submit">Criar evento</button>
                </form>
              </Panel>
              <Panel title="Eventos criados">
                <div className="grid gap-3">
                  {events.slice(0, 8).map((event) => {
                    const eventBuildCount = builds.filter((build) => build.event_slots.some((slot) => slot.event_id === event.id)).length;
                    const editing = eventEditForm.eventId === String(event.id);
                    return (
                      <div className="rounded border border-zinc-800 bg-zinc-950 p-3" key={event.id}>
                        {editing ? (
                          <form className="grid gap-2" onSubmit={saveEventEdit}>
                            <input className="control h-9" onChange={(item) => setEventEditForm({ ...eventEditForm, title: item.target.value })} required value={eventEditForm.title} />
                            <input className="control h-9" onChange={(item) => setEventEditForm({ ...eventEditForm, eventDate: item.target.value })} required type="datetime-local" value={eventEditForm.eventDate} />
                            <div className="grid gap-2 sm:grid-cols-2">
                              <select className="control h-9" onChange={(item) => setEventEditForm({ ...eventEditForm, contentType: item.target.value })} value={eventEditForm.contentType}>
                                {contentTypes.map((item) => <option key={item} value={item}>{item}</option>)}
                              </select>
                              <select className="control h-9" onChange={(item) => setEventEditForm({ ...eventEditForm, status: item.target.value })} value={eventEditForm.status}>
                                <option value="open">Aberto</option>
                                <option value="draft">Rascunho</option>
                                <option value="closed">Fechado</option>
                              </select>
                            </div>
                            <input className="control h-9" min={0} onChange={(item) => setEventEditForm({ ...eventEditForm, mountGallopRequirement: item.target.value })} type="number" value={eventEditForm.mountGallopRequirement} />
                            <textarea className="control min-h-16 py-2" onChange={(item) => setEventEditForm({ ...eventEditForm, mountRequirementNote: item.target.value })} value={eventEditForm.mountRequirementNote} />
                            <div className="flex flex-wrap gap-2">
                              <button className="button-primary h-9" disabled={saving} type="submit">Salvar</button>
                              <button className="button-secondary h-9" disabled={saving} onClick={() => setEventEditForm({ ...eventEditForm, eventId: '' })} type="button">Cancelar</button>
                            </div>
                          </form>
                        ) : (
                          <>
                            <div className="grid gap-2 sm:grid-cols-[1fr_auto] sm:items-start">
                              <div className="min-w-0">
                                <p className="truncate text-sm font-semibold text-zinc-100">{event.title}</p>
                                <p className="mt-1 text-xs text-zinc-500">
                                  {event.content_type} / {formatDate(event.event_date)} / {event.status} / {eventBuildCount} build(s)
                                </p>
                              </div>
                              <span className={event.status === 'closed' ? 'text-xs font-semibold text-red-300' : 'text-xs font-semibold text-emerald-300'}>
                                {event.status === 'closed' ? 'Fechado' : 'Aberto'}
                              </span>
                            </div>
                            <div className="mt-3 flex flex-wrap gap-2">
                              <button
                                className="button-primary h-9"
                                onClick={() => {
                                  setEventManageForm({ eventId: String(event.id), buildId: '', slots: '1' });
                                  setView('eventBuilds');
                                }}
                                type="button"
                              >
                                Compor
                              </button>
                              <button className="button-secondary h-9" disabled={saving} onClick={() => startEventEdit(event)} type="button">
                                Editar
                              </button>
                              <button className="button-secondary h-9" disabled={saving} onClick={() => void duplicateEvent(event)} type="button">
                                Duplicar base
                              </button>
                              <button
                                className="button-secondary h-9"
                                disabled={saving}
                                onClick={() => void setEventStatus(event, event.status === 'closed' ? 'open' : 'closed')}
                                type="button"
                              >
                                {event.status === 'closed' ? 'Reabrir' : 'Fechar'}
                              </button>
                            </div>
                          </>
                        )}
                      </div>
                    );
                  })}
                  {!events.length ? <p className="text-sm text-zinc-500">Nenhum evento criado ainda.</p> : null}
                </div>
              </Panel>
              <Panel title="Ranking">
                <div className="space-y-3">
                  {ranking.slice(0, 6).map((player, index) => (
                    <div className="grid grid-cols-[2rem_1fr_auto] items-center gap-3 rounded-md border border-zinc-800 bg-zinc-950/60 px-3 py-2" key={player.id}>
                      <span className="text-sm font-bold text-red-400">#{index + 1}</span>
                      <span className="min-w-0 truncate text-sm font-semibold">{player.albion_nick}</span>
                      <span className="text-xs text-zinc-400">{player.participations} pres. / {player.rating.toFixed(1)}</span>
                    </div>
                  ))}
                </div>
              </Panel>
            </div>
          </section>
        ) : null}

        {view === 'eventBuilds' && canManage ? (
          <section className="grid gap-5 xl:grid-cols-[0.85fr_1.15fr]">
            <Panel title="Selecionar evento para compor">
              <div className="grid gap-3">
                <select
                  className="control"
                  onChange={(event) => setEventManageForm({ eventId: event.target.value, buildId: '', slots: '1' })}
                  value={eventManageForm.eventId}
                >
                  <option value="">Selecione um evento</option>
                  {events.filter((event) => event.status !== 'closed').map((event) => (
                    <option key={event.id} value={event.id}>
                      {event.title} - {formatDate(event.event_date)} - {event.status}
                    </option>
                  ))}
                </select>

                {selectedManagedEvent ? (
                  <div className="rounded border border-zinc-800 bg-zinc-950 p-4 text-sm text-zinc-300">
                    <p className="text-base font-bold text-zinc-100">{selectedManagedEvent.title}</p>
                    <p className="mt-1 text-xs text-zinc-500">
                      {selectedManagedEvent.content_type} / {formatDate(selectedManagedEvent.event_date)} / {selectedManagedEvent.status}
                    </p>
                    <p className="mt-2 text-xs font-semibold text-emerald-300">
                      Montaria: galope {selectedManagedEvent.mount_gallop_requirement ?? 120}%+
                    </p>
                    {selectedManagedEvent.mount_requirement_note ? (
                      <p className="mt-2 text-xs text-zinc-400">{selectedManagedEvent.mount_requirement_note}</p>
                    ) : null}
                    <div className="mt-3 flex flex-wrap gap-2">
                      <button className="button-secondary h-9" disabled={saving} onClick={() => void duplicateEvent(selectedManagedEvent)} type="button">
                        Duplicar como base
                      </button>
                      <button
                        className="button-secondary h-9"
                        disabled={saving}
                        onClick={() => void setEventStatus(selectedManagedEvent, selectedManagedEvent.status === 'closed' ? 'open' : 'closed')}
                        type="button"
                      >
                        {selectedManagedEvent.status === 'closed' ? 'Reabrir evento' : 'Fechar evento'}
                      </button>
                    </div>
                  </div>
                ) : null}

                {selectedManagedEvent ? (
                  <form className="grid gap-2 sm:grid-cols-[1fr_5rem_auto]" onSubmit={linkBuildToManagedEvent}>
                    <select
                      className="control"
                      onChange={(event) => setEventManageForm({ ...eventManageForm, buildId: event.target.value })}
                      required
                      value={eventManageForm.buildId}
                    >
                      <option value="">Selecionar build cadastrada</option>
                      {builds
                        .filter((build) => build.active && !build.event_slots.some((slot) => slot.event_id === selectedManagedEvent.id))
                        .map((build) => (
                          <option key={build.id} value={build.id}>
                            {build.name} / {build.role}
                          </option>
                        ))}
                    </select>
                    <input
                      className="control"
                      min={1}
                      onChange={(event) => setEventManageForm({ ...eventManageForm, slots: event.target.value })}
                      type="number"
                      value={eventManageForm.slots}
                    />
                    <button className="button-primary" disabled={saving || selectedManagedEvent.status === 'closed'} type="submit">Vincular</button>
                  </form>
                ) : null}
              </div>
            </Panel>

            <Panel title="Builds e vagas do evento">
              {selectedManagedEvent ? (
                <div className="grid gap-3">
                  {managedEventBuilds.map(({ build, slot }) => (
                    <div className="grid gap-3 rounded border border-zinc-800 bg-zinc-950 p-3" key={build.id}>
                      <div className="flex items-start gap-3">
                        {build.weapon_icon_url ? <img alt="" className="h-12 w-12 rounded bg-zinc-900 object-contain" src={build.weapon_icon_url} /> : null}
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-semibold text-zinc-100">{build.name}</p>
                          <p className="text-xs text-zinc-500">{build.role} / {build.weapon_name}</p>
                          <p className={`mt-1 text-xs font-semibold ${slotTone(slot)}`}>
                            {slot?.remaining_slots ?? 0} faltando / {slotLabel(slot)}
                          </p>
                        </div>
                      </div>
                      <div className="grid gap-2 sm:grid-cols-[1fr_auto]">
                        <input
                          className="control h-9"
                          defaultValue={slot?.max_slots ?? 1}
                          disabled={selectedManagedEvent.status === 'closed'}
                          min={1}
                          onBlur={(event) => void changeManagedBuildSlots(build, selectedManagedEvent.id, Number(event.target.value || 1))}
                          type="number"
                        />
                        <button
                          className="button-secondary h-9"
                          disabled={saving || selectedManagedEvent.status === 'closed'}
                          onClick={() => void unlinkBuildFromManagedEvent(build, selectedManagedEvent.id)}
                          type="button"
                        >
                          Remover
                        </button>
                      </div>
                    </div>
                  ))}
                  {!managedEventBuilds.length ? <p className="text-sm text-zinc-500">Nenhuma build selecionada para este evento.</p> : null}
                </div>
              ) : (
                <p className="text-sm text-zinc-500">Selecione um evento para montar a composicao.</p>
              )}
            </Panel>
          </section>
        ) : null}

        {view === 'eventManage' && canManage ? (
          <section className="grid gap-5">
            <Panel title="Selecionar evento para gerenciar">
              <div className="grid gap-3 lg:grid-cols-[1fr_auto_auto_auto_auto] lg:items-center">
                <select
                  className="control"
                  onChange={(event) => setEventManageForm({ eventId: event.target.value, buildId: '', slots: '1' })}
                  value={eventManageForm.eventId}
                >
                  <option value="">Selecione um evento</option>
                  {events.filter((event) => event.status !== 'closed').map((event) => (
                    <option key={event.id} value={event.id}>
                      {event.title} - {formatDate(event.event_date)}
                    </option>
                  ))}
                </select>
                <Metric label="Check-ins" value={managedEventCheckins.length} compact />
                <Metric label="Confirmados" value={managedEventConfirmed} compact />
                <Metric label="Pendentes" value={managedEventCheckins.length - managedEventConfirmed} compact />
                <button className="button-secondary h-9" disabled={loading} onClick={() => void loadData()} type="button">Atualizar</button>
              </div>
            </Panel>

            {selectedManagedEvent ? (
              <section className="grid gap-5 xl:grid-cols-[0.75fr_1.25fr]">
                <div className="space-y-5">
                  <Panel title="Evento selecionado">
                    <div className="grid gap-3">
                      <div className="rounded border border-red-950/60 bg-zinc-950/80 p-4">
                        <p className="text-lg font-bold text-white">{selectedManagedEvent.title}</p>
                        <p className="mt-1 text-sm text-zinc-400">
                          {selectedManagedEvent.content_type} / {formatDate(selectedManagedEvent.event_date)} / {selectedManagedEvent.status}
                        </p>
                        <p className="mt-2 text-xs font-semibold text-emerald-300">
                          Montaria: galope {selectedManagedEvent.mount_gallop_requirement ?? 120}%+
                        </p>
                        {selectedManagedEvent.mount_requirement_note ? (
                          <p className="mt-2 text-sm text-zinc-400">{selectedManagedEvent.mount_requirement_note}</p>
                        ) : null}
                      </div>
                    </div>
                  </Panel>

                  <Panel title="Composicao e vagas">
                    <div className="grid gap-3">
                      {managedEventBuilds.map(({ build, slot }) => (
                        <div className="grid gap-2 rounded border border-zinc-800 bg-zinc-950/70 p-3" key={build.id}>
                          <div className="flex items-start gap-3">
                            {build.weapon_icon_url ? <img alt="" className="h-12 w-12 rounded bg-zinc-900 object-contain" src={build.weapon_icon_url} /> : null}
                            <div className="min-w-0 flex-1">
                              <p className="truncate text-sm font-semibold text-zinc-100">{build.name}</p>
                              <p className="text-xs text-zinc-500">{build.role} / {build.weapon_name}</p>
                              <p className={`mt-1 text-xs font-semibold ${slotTone(slot)}`}>
                                {slot?.remaining_slots ?? 0} faltando / {slotLabel(slot)}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                      {!managedEventBuilds.length ? <p className="text-sm text-zinc-500">Nenhuma build configurada para este evento.</p> : null}
                    </div>
                  </Panel>
                </div>

                <div className="grid gap-5">
                  <Panel title="Solicitacoes de DG deste evento">
                    <div className="grid gap-3">
                      {managedEventPendingRequests.map((buildRequest) => (
                        <div className="item-card" key={buildRequest.id}>
                          <div className="grid gap-3 lg:grid-cols-[auto_1fr_auto] lg:items-center">
                            {buildRequest.build_icon_url ? (
                              <img alt="" className="h-12 w-12 rounded bg-zinc-900 object-contain" src={buildRequest.build_icon_url} />
                            ) : <span className="h-12 w-12 rounded bg-zinc-900" />}
                            <div className="min-w-0">
                              <p className="truncate text-sm font-semibold text-white">{buildRequest.player_nick ?? `Player ${buildRequest.player_id}`}</p>
                              <p className="text-xs text-zinc-400">{buildRequest.build_name ?? `Build ${buildRequest.build_id}`} / {buildRequest.build_role ?? 'Funcao nao informada'}</p>
                              <p className="mt-1 text-xs text-zinc-500">{buildRequest.weapon_power != null ? `IP da arma: ${buildRequest.weapon_power}` : 'IP da arma: nao informado'}</p>
                              <p className="mt-1 text-xs text-zinc-500">Solicitado em {formatDate(buildRequest.created_at)}</p>
                            </div>
                            <div className="flex flex-wrap gap-2 lg:justify-end">
                              <button className="button-primary h-9" disabled={saving} onClick={() => void decideBuildRequest(buildRequest, 'approved')} type="button">
                                Aprovar
                              </button>
                              <button className="button-secondary h-9" disabled={saving} onClick={() => void decideBuildRequest(buildRequest, 'rejected')} type="button">
                                Rejeitar
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                      {!managedEventPendingRequests.length ? (
                        <p className="text-sm text-zinc-500">Nenhuma solicitacao pendente para este evento.</p>
                      ) : null}
                    </div>
                  </Panel>

                  <Panel title="Grupo que fez check-in">
                    <div className="grid gap-4">
                    {managedEventCheckinsByBuild.map(({ buildName, rows }) => (
                      <div className="rounded border border-zinc-800 bg-zinc-950/70" key={buildName}>
                        <div className="grid grid-cols-[1fr_auto] gap-3 border-b border-zinc-800 px-4 py-3">
                          <p className="min-w-0 truncate text-sm font-bold text-zinc-100">{buildName}</p>
                          <span className="text-xs font-semibold text-red-400">{rows.length} player(s)</span>
                        </div>
                        <div className="divide-y divide-zinc-800/80">
                          {rows.map((checkin) => {
                            const mount = mountsByName.get(checkin.mount_selected);
                            return (
                              <div className="grid gap-3 px-4 py-3 lg:grid-cols-[1.2fr_1fr_1fr_auto] lg:items-center" key={checkin.id}>
                                <div className="min-w-0">
                                  <p className="truncate text-sm font-semibold text-white">{checkin.player_nick ?? checkin.user_id}</p>
                                  <p className="text-xs text-zinc-500">{checkin.build_role ?? 'Funcao nao informada'} / {formatDate(checkin.checkin_time)}</p>
                                </div>
                                <p className="text-sm text-zinc-300">{mount ? mountLabel(mount) : checkin.mount_selected}</p>
                                <span className={checkin.approved ? 'text-sm font-semibold text-emerald-300' : 'text-sm font-semibold text-red-300'}>
                                  {checkin.approved ? 'Confirmado' : 'Pendente'}
                                </span>
                                <div className="flex flex-wrap justify-start gap-2 lg:justify-end">
                                  <button
                                    className={checkin.approved ? 'button-secondary h-9' : 'button-primary h-9'}
                                    disabled={saving}
                                    onClick={() => void toggleCheckinStatus(checkin)}
                                    type="button"
                                  >
                                    {checkin.approved ? 'Marcar pendente' : 'Confirmar'}
                                  </button>
                                  <button
                                    className="button-secondary h-9"
                                    disabled={saving}
                                    onClick={() => void removeCheckinFromEvent(checkin)}
                                    type="button"
                                  >
                                    Remover
                                  </button>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    ))}
                    {!managedEventCheckinsByBuild.length ? (
                      <p className="text-sm text-zinc-500">Nenhum player fez check-in neste evento ainda.</p>
                    ) : null}
                    </div>
                  </Panel>
                </div>
              </section>
            ) : (
              <Panel title="Nenhum evento selecionado">
                <p className="text-sm text-zinc-500">Selecione um evento acima para ver e gerenciar o grupo que fez check-in.</p>
              </Panel>
            )}
          </section>
        ) : null}

        {view === 'builds' && canManage ? (
          <section className="grid gap-5 xl:grid-cols-[0.85fr_1.15fr]">
            <Panel title="Criar build">
              <form className="grid gap-3" onSubmit={createBuild}>
                <input className="control" onChange={(event) => setBuildForm({ ...buildForm, name: event.target.value })} placeholder="Build CTA - Shadowcaller" required value={buildForm.name} />
                <select className="control" onChange={(event) => setBuildForm({ ...buildForm, buildType: event.target.value })} value={buildForm.buildType}>
                  {contentTypes.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
                <select className="control" onChange={(event) => setBuildForm({ ...buildForm, role: event.target.value })} value={buildForm.role}>
                  {roles.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
                <div className="grid gap-3 md:grid-cols-[1.4fr_0.7fr_0.7fr]">
                  <select className="control" onChange={(event) => chooseAlbionWeapon(event.target.value)} required value={buildForm.weaponBaseName}>
                    <option value="">Arma do Albion</option>
                    {albionWeapons.map((weapon) => (
                      <option key={weapon.name_en ?? weapon.name} value={weapon.name}>
                        {weapon.name}{weapon.name_en && weapon.name_en !== weapon.name ? ` / ${weapon.name_en}` : ''}
                      </option>
                    ))}
                  </select>
                  <select className="control" disabled={!selectedAlbionWeapon} onChange={(event) => chooseWeaponVariant(event.target.value)} required value={buildForm.weaponTier}>
                    <option value="">Tier</option>
                    {(selectedAlbionWeapon?.variants ?? []).map((variant) => (
                      <option key={`${variant.item_id}-${variant.tier}`} value={variant.tier ?? ''}>T{variant.tier}</option>
                    ))}
                  </select>
                  <select className="control" disabled={!selectedAlbionWeapon} onChange={(event) => chooseWeaponVariant(buildForm.weaponTier, event.target.value)} value={buildForm.weaponEnchant}>
                    {enchantments.map((enchant) => (
                      <option key={enchant} value={enchant}>{enchant === '0' ? 'Sem encanto' : `.${enchant}`}</option>
                    ))}
                  </select>
                </div>
                {buildForm.weaponIconUrl ? (
                  <div className="flex items-center gap-3 rounded border border-zinc-800 bg-zinc-950 p-3">
                    <img alt="" className="h-16 w-16 rounded bg-zinc-900 object-contain" src={buildForm.weaponIconUrl} />
                    <div>
                      <p className="text-sm font-semibold">{buildForm.weaponName}</p>
                      <p className="text-xs text-zinc-500">Tier {buildForm.weaponTier}, encantamento {buildForm.weaponEnchant}. Imagem renderizada pelo Albion.</p>
                    </div>
                  </div>
                ) : null}
                <div className="grid gap-3">
                  {gearSelector('offhand', 'Offhand', offhandOptions)}
                  {gearSelector('helmet', 'Capacete', helmetOptions)}
                  {gearSelector('chest', 'Peitoral', chestOptions)}
                  {gearSelector('boots', 'Bota', bootsOptions)}
                </div>
                <div className="grid gap-3 md:grid-cols-2">
                  <input className="control" onChange={(event) => setBuildForm({ ...buildForm, cape: event.target.value })} placeholder="Capa" value={buildForm.cape} />
                  <input className="control" onChange={(event) => setBuildForm({ ...buildForm, food: event.target.value })} placeholder="Comida" value={buildForm.food} />
                  <input className="control" onChange={(event) => setBuildForm({ ...buildForm, potion: event.target.value })} placeholder="Pocao" value={buildForm.potion} />
                  <input className="control" onChange={(event) => setBuildForm({ ...buildForm, requiredLevel: event.target.value })} placeholder="Nivel requerido" type="number" value={buildForm.requiredLevel} />
                </div>
                <select className="control" onChange={(event) => setBuildForm({ ...buildForm, recommendedMount: event.target.value })} value={buildForm.recommendedMount}>
                  <option value="">Montaria recomendada</option>
                  {mounts.map((mount) => <option key={mount.mount_name} value={mount.mount_name}>{mountLabel(mount)} - {mountDetail(mount)}</option>)}
                </select>
                {recommendedMount ? (
                  <div className="flex items-center gap-3 rounded border border-zinc-800 bg-zinc-950 p-3">
                    {recommendedMount.icon_url ? <img alt="" className="h-14 w-14 rounded bg-zinc-900 object-contain" src={recommendedMount.icon_url} /> : null}
                    <div>
                      <p className="text-sm font-semibold">{mountLabel(recommendedMount)}</p>
                      <p className="text-xs text-zinc-500">{mountDetail(recommendedMount)}</p>
                    </div>
                  </div>
                ) : null}
                <textarea className="control min-h-24 py-3" onChange={(event) => setBuildForm({ ...buildForm, description: event.target.value })} placeholder="Observacoes e instrucoes para a PT" value={buildForm.description} />
                <button className="button-primary" disabled={saving} type="submit">Salvar build</button>
              </form>
            </Panel>

            <div className="space-y-5">
              <Panel title="Builds configuradas">
                <div className="grid gap-3 md:grid-cols-2">
                  {builds.map((build) => (
                    <div className="item-card" key={build.id}>
                      <div className="flex gap-3">
                        {build.weapon_icon_url ? <img alt="" className="h-14 w-14 rounded bg-zinc-900 object-contain" src={build.weapon_icon_url} /> : null}
                        <div className="min-w-0">
                          <p className="truncate font-semibold">{build.name}</p>
                          <p className="text-sm text-zinc-400">{build.build_type} / {build.role} / {build.weapon_name}</p>
                          <p className="mt-1 text-xs text-zinc-500">{build.active ? 'ativa' : 'inativa'} / liberacao por jogador nesta aba</p>
                        </div>
                      </div>
                      <div className="mt-3 grid gap-1 text-xs text-zinc-400">
                        <div className="flex flex-wrap gap-2">
                          {[build.offhand_icon_url, build.helmet_icon_url, build.chest_icon_url, build.boots_icon_url].filter(Boolean).map((icon) => (
                            <img alt="" className="h-9 w-9 rounded bg-zinc-900 object-contain" key={icon} src={icon ?? ''} />
                          ))}
                        </div>
                        <span>Equip: {[build.offhand, build.helmet, build.chest, build.boots, build.cape].filter(Boolean).join(' / ') || 'Nao informado'}</span>
                        <span>Consumiveis: {[build.food, build.potion].filter(Boolean).join(' / ') || 'Nao informado'}</span>
                        {build.recommended_mount ? (() => {
                          const mount = mountsByName.get(build.recommended_mount || '');
                          return <span>Montaria sugerida: {mount ? `${mountLabel(mount)} (${mountDetail(mount)})` : build.recommended_mount}</span>;
                        })() : null}
                      </div>
                      <div className="mt-3 flex gap-2">
                        {build.active ? (
                          <button className="button-secondary h-9" disabled={saving} onClick={() => void deactivateBuild(build)} type="button">Inativar</button>
                        ) : (
                          <button className="button-primary h-9" disabled={saving} onClick={() => void reactivateBuild(build)} type="button">Reativar</button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </Panel>

              <Panel title="Liberar builds por jogador">
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[760px] border-collapse text-sm">
                    <thead>
                      <tr className="border-b border-zinc-800 text-left text-xs uppercase text-zinc-500">
                        <th className="py-3">Jogador</th>
                        {builds.map((build) => <th key={build.id}>{build.name}</th>)}
                      </tr>
                    </thead>
                    <tbody>
                      {players.filter((player) => player.active).map((player) => (
                        <tr className="border-b border-zinc-800/70" key={player.id}>
                          <td className="py-3 font-semibold">{player.albion_nick}</td>
                          {builds.map((build) => {
                            const approved = approvals.some((approval) => approval.player_id === player.id && approval.build_id === build.id && approval.approved);
                            return (
                              <td key={build.id}>
                                <button className={approved ? 'button-primary h-9' : 'button-secondary h-9'} disabled={saving} onClick={() => toggleApproval(player, build)} type="button">
                                  {approved ? 'Liberada' : 'Bloqueada'}
                                </button>
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Panel>
            </div>
          </section>
        ) : null}

        {view === 'leader' && canLead ? (
          <section className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
            <Panel title="Solicitacoes pendentes de DG">
              <div className="grid gap-3">
                {pendingBuildRequests.map((buildRequest) => (
                  <div className="item-card" key={buildRequest.id}>
                    <div className="grid gap-3 lg:grid-cols-[auto_1fr_auto] lg:items-center">
                      {buildRequest.build_icon_url ? (
                        <img alt="" className="h-14 w-14 rounded bg-zinc-900 object-contain" src={buildRequest.build_icon_url} />
                      ) : <span className="h-14 w-14 rounded bg-zinc-900" />}
                      <div className="min-w-0">
                        <p className="truncate font-semibold text-white">{buildRequest.player_nick ?? `Player ${buildRequest.player_id}`}</p>
                        <p className="text-sm text-zinc-400">
                          {buildRequest.event_title ?? `Evento ${buildRequest.event_id}`} / {buildRequest.build_name ?? `Build ${buildRequest.build_id}`}
                        </p>
                        <p className="mt-1 text-xs text-zinc-500">
                          {buildRequest.weapon_power != null ? `IP da arma: ${buildRequest.weapon_power}` : 'IP da arma: nao informado'}
                        </p>
                        <p className="mt-1 text-xs text-zinc-500">
                          {buildRequest.build_role ?? 'Funcao nao informada'} / solicitado em {formatDate(buildRequest.created_at)}
                        </p>
                      </div>
                      <div className="flex flex-wrap gap-2 lg:justify-end">
                        <button className="button-primary h-9" disabled={saving} onClick={() => void decideBuildRequest(buildRequest, 'approved')} type="button">
                          Aprovar
                        </button>
                        <button className="button-secondary h-9" disabled={saving} onClick={() => void decideBuildRequest(buildRequest, 'rejected')} type="button">
                          Rejeitar
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
                {!pendingBuildRequests.length ? <p className="text-sm text-zinc-500">Nenhuma solicitacao pendente.</p> : null}
              </div>
            </Panel>

            <Panel title="Historico de solicitacoes">
              <div className="grid gap-2">
                {buildRequests.filter((request) => request.status !== 'pending').slice(0, 12).map((buildRequest) => (
                  <div className="grid grid-cols-[1fr_auto] gap-3 rounded border border-zinc-800 bg-zinc-950/70 px-3 py-2 text-sm" key={buildRequest.id}>
                    <span className="min-w-0 truncate text-zinc-300">
                      {buildRequest.player_nick ?? buildRequest.player_id} / {buildRequest.build_name ?? buildRequest.build_id}
                    </span>
                    <span className={buildRequest.status === 'approved' ? 'font-semibold text-emerald-300' : 'font-semibold text-red-300'}>
                      {buildRequest.status === 'approved' ? 'Aprovada' : 'Rejeitada'}
                    </span>
                  </div>
                ))}
                {!buildRequests.filter((request) => request.status !== 'pending').length ? (
                  <p className="text-sm text-zinc-500">Sem historico ainda.</p>
                ) : null}
              </div>
            </Panel>
          </section>
        ) : null}

        {view === 'checkin' ? (
          <section className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
            <Panel title="Participar do ZvZ">
              <form className="grid gap-3" onSubmit={submitCheckin}>
                <input
                  className="control"
                  onChange={(event) => setCheckinForm({ ...checkinForm, nick: event.target.value, buildId: '', mount: '' })}
                  placeholder="Nick Albion"
                  required
                  value={checkinForm.nick}
                />
                {authSession ? (
                  <p className="text-xs text-zinc-500">Nick carregado do seu perfil Discord. Edite e salve acima caso precise corrigir.</p>
                ) : null}
                <select className="control" onChange={(event) => setCheckinForm({ ...checkinForm, eventId: event.target.value, buildId: '', mount: '' })} required value={checkinForm.eventId}>
                  <option value="">Selecione o evento</option>
                  {events.filter((event) => event.status !== 'closed').map((event) => (
                    <option key={event.id} value={event.id}>{event.title} - {formatDate(event.event_date)}</option>
                  ))}
                </select>
                {selectedCheckinEvent ? (
                  <div className="rounded border border-zinc-800 bg-zinc-950 p-3 text-sm text-zinc-300">
                    {selectedCheckinEventIsDungeon ? (
                      <>
                        <p className="font-semibold text-zinc-100">DG: escolha uma build e envie solicitacao ao lider.</p>
                        <p className="mt-1 text-xs text-zinc-500">Quando um lider aprovar, voce entra no grupo/check-in do evento.</p>
                      </>
                    ) : (
                      <>
                        <p className="font-semibold text-zinc-100">Montaria: galope {selectedCheckinEvent.mount_gallop_requirement ?? 120}%+</p>
                        {selectedCheckinEvent.mount_requirement_note ? (
                          <p className="mt-1 text-xs text-zinc-500">{selectedCheckinEvent.mount_requirement_note}</p>
                        ) : null}
                      </>
                    )}
                  </div>
                ) : null}
                {!selectedCheckinEventIsDungeon ? (
                  <>
                    <select className="control" disabled={!availableBuilds.length} onChange={(event) => setCheckinForm({ ...checkinForm, buildId: event.target.value, mount: '' })} required value={checkinForm.buildId}>
                      <option value="">Build liberada</option>
                      {availableBuilds.map((build) => {
                        const slot = build.event_slots.find((item) => String(item.event_id) === checkinForm.eventId);
                        return <option key={build.id} value={build.id}>{build.name} - {slot?.remaining_slots ?? 0} vaga(s)</option>;
                      })}
                    </select>
                    {selectedCheckinSlot ? (
                      <div className="rounded border border-emerald-400/30 bg-emerald-400/10 px-3 py-2 text-sm text-emerald-100">
                        {selectedCheckinSlot.remaining_slots} vaga(s) restantes nesta build. {slotLabel(selectedCheckinSlot)}.
                      </div>
                    ) : null}
                    <select className="control" disabled={!selectedCheckinBuild} onChange={(event) => setCheckinForm({ ...checkinForm, mount: event.target.value })} required value={checkinForm.mount}>
                      <option value="">Montaria com galope suficiente</option>
                      {checkinMountOptions.map((mountName) => {
                        const mount = mountsByName.get(mountName);
                        return <option key={mountName} value={mountName}>{mount ? `${mountLabel(mount)} - ${mountDetail(mount)}` : mountName}</option>;
                      })}
                    </select>
                    {selectedCheckinMount ? (
                      <div className="flex items-center gap-3 rounded border border-zinc-800 bg-zinc-950 p-3">
                        {selectedCheckinMount.icon_url ? <img alt="" className="h-14 w-14 rounded bg-zinc-900 object-contain" src={selectedCheckinMount.icon_url} /> : null}
                        <div>
                          <p className="text-sm font-semibold">{mountLabel(selectedCheckinMount)}</p>
                          <p className="text-xs text-zinc-500">{mountDetail(selectedCheckinMount)}</p>
                        </div>
                      </div>
                    ) : null}
                    <button className="button-primary" disabled={saving || !selectedCheckinBuild} type="submit">Confirmar check-in</button>
                  </>
                ) : (
                  <div className="rounded border border-red-400/30 bg-red-400/10 px-3 py-2 text-sm text-red-100">
                    Clique em uma build ao lado para enviar a solicitacao ao lider.
                    {!authSession ? ' E necessario entrar com Discord.' : null}
                  </div>
                )}
              </form>
            </Panel>
            <Panel title={selectedCheckinEventIsDungeon ? 'Builds para solicitar ao lider' : 'Builds disponiveis para o nick'}>
              {selectedCheckinEventIsDungeon ? (
                <div className="mb-3 rounded border border-zinc-800 bg-zinc-950/70 p-3">
                  <label className="block text-sm text-zinc-400" htmlFor="request-weapon-power">
                    <span className="mb-1 block">IP da arma</span>
                    <input
                      className="control h-9"
                      id="request-weapon-power"
                      min={0}
                      onChange={(event) => setRequestWeaponPower(event.target.value)}
                      placeholder="Ex: 1400"
                      type="number"
                      value={requestWeaponPower}
                    />
                  </label>
                  <p className="mt-1 text-xs text-zinc-500">O líder verá esse valor na gestão das solicitações.</p>
                </div>
              ) : null}
              <div className="grid gap-3 md:grid-cols-2">
                {availableBuilds.map((build) => {
                  const requestForBuild = buildRequests.find(
                    (request) => request.event_id === Number(checkinForm.eventId) && request.build_id === build.id && request.player_id === authSession?.userId,
                  );
                  return (
                    <div className="item-card" key={build.id}>
                      <div className="flex gap-3">
                        {build.weapon_icon_url ? <img alt="" className="h-14 w-14 rounded bg-zinc-900 object-contain" src={build.weapon_icon_url} /> : null}
                        <div>
                          <p className="font-semibold">{build.name}</p>
                          <p className="text-sm text-zinc-400">{build.role} / {build.weapon_name}</p>
                          {!selectedCheckinEventIsDungeon ? (() => {
                            const slot = build.event_slots.find((item) => String(item.event_id) === checkinForm.eventId);
                            return <p className={`mt-1 text-xs font-semibold ${slotTone(slot)}`}>{slot?.remaining_slots ?? 0} vaga(s) restantes / {slotLabel(slot)}</p>;
                          })() : (
                            <p className="mt-1 text-xs text-zinc-500">
                              {requestForBuild ? `Solicitacao: ${requestForBuild.status}` : 'Clique para solicitar esta build'}
                            </p>
                          )}
                          {(() => {
                            const mount = mountsByName.get(build.recommended_mount || '');
                            return build.recommended_mount ? <p className="mt-1 text-xs text-zinc-500">Montaria sugerida: {mount ? `${mountLabel(mount)} - ${mountDetail(mount)}` : build.recommended_mount}</p> : null;
                          })()}
                        </div>
                      </div>
                      <div className="mt-3 text-xs text-zinc-400">
                        <div className="mb-2 flex flex-wrap gap-2">
                          {[build.offhand_icon_url, build.helmet_icon_url, build.chest_icon_url, build.boots_icon_url].filter(Boolean).map((icon) => (
                            <img alt="" className="h-9 w-9 rounded bg-zinc-900 object-contain" key={icon} src={icon ?? ''} />
                          ))}
                        </div>
                        {[build.helmet, build.chest, build.boots, build.cape, build.food, build.potion].filter(Boolean).join(' / ') || 'Equipamentos complementares nao informados'}
                      </div>
                      {selectedCheckinEventIsDungeon ? (
                        <button
                          className="button-primary mt-3 h-9"
                          disabled={saving || !authSession || Boolean(requestForBuild)}
                          onClick={() => void requestDungeonBuild(build)}
                          type="button"
                        >
                          {requestForBuild ? 'Solicitado' : 'Solicitar ao lider'}
                        </button>
                      ) : null}
                    </div>
                  );
                })}
                {!availableBuilds.length ? (
                  <p className="text-sm text-zinc-400">
                    {selectedCheckinEventIsDungeon ? 'Nenhuma build ativa cadastrada para solicitar.' : 'Informe nick e evento para ver builds autorizadas.'}
                  </p>
                ) : null}
              </div>
            </Panel>
          </section>
        ) : null}

        {view === 'settings' && canManage ? (
          <section className="grid gap-5 xl:grid-cols-[0.75fr_1.25fr]">
            <Panel title="Adicionar player">
              <form className="grid gap-3" onSubmit={createPlayer}>
                <input className="control" onChange={(event) => setPlayerForm({ albionNick: event.target.value })} placeholder="Nick Albion" required value={playerForm.albionNick} />
                <button className="button-primary" disabled={saving} type="submit">Adicionar como membro</button>
              </form>
              <p className="mt-3 text-xs text-zinc-500">
                Novos jogadores entram como membros normais. O historico fica preservado quando um player e inativado.
              </p>
            </Panel>

            <Panel title="Permissoes e players">
              <div className="overflow-x-auto">
                <table className="w-full min-w-[920px] border-collapse text-sm">
                  <thead>
                    <tr className="border-b border-zinc-800 text-left text-xs uppercase text-zinc-500">
                      <th className="py-3">Player</th>
                      <th>Discord</th>
                      <th>Status</th>
                      <th>Acesso</th>
                      <th>Ranking</th>
                      <th>Acoes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {players.map((player) => (
                      <tr className="border-b border-zinc-800/70" key={player.id}>
                        <td className="py-3">
                          <p className="font-semibold text-zinc-100">{player.albion_nick}</p>
                          <p className="text-xs text-zinc-500">ID {player.id}</p>
                        </td>
                        <td>{player.discord_name || player.discord_id || 'Nao vinculado'}</td>
                        <td>
                          <span className={player.active ? 'text-emerald-300' : 'text-red-300'}>
                            {player.active ? 'Ativo' : 'Inativo'}
                          </span>
                        </td>
                        <td>
                          <div className="flex flex-wrap gap-2">
                            <select
                              className="control h-9 w-32"
                              disabled={saving || player.role === 'dev'}
                              onChange={(event) => void updatePlayerAccess(player, {
                                role: event.target.value,
                                is_staff: event.target.value === 'staff' || event.target.value === 'dev',
                                is_leader: event.target.value === 'leader' || event.target.value === 'staff' || event.target.value === 'dev',
                              })}
                              value={player.role}
                            >
                              <option value="player">Membro</option>
                              <option value="leader">Lider</option>
                              <option value="staff">Staff</option>
                              <option value="dev">Dev</option>
                            </select>
                            <button
                              className={player.is_staff ? 'button-primary h-9' : 'button-secondary h-9'}
                              disabled={saving || player.role === 'dev'}
                              onClick={() => void updatePlayerAccess(player, {
                                is_staff: !player.is_staff,
                                role: !player.is_staff ? 'staff' : 'player',
                                is_leader: !player.is_staff,
                              })}
                              type="button"
                            >
                              {player.is_staff ? 'Staff' : 'Membro'}
                            </button>
                            <button
                              className={player.is_leader ? 'button-primary h-9' : 'button-secondary h-9'}
                              disabled={saving || player.role === 'dev' || player.is_staff}
                              onClick={() => void updatePlayerAccess(player, {
                                is_leader: !player.is_leader,
                                role: !player.is_leader ? 'leader' : 'player',
                              })}
                              type="button"
                            >
                              {player.is_leader ? 'Lider' : 'Nao lider'}
                            </button>
                          </div>
                        </td>
                        <td>{player.participations} pres. / {player.rating.toFixed(1)}</td>
                        <td>
                          {player.active ? (
                            <button
                              className="button-secondary h-9"
                              disabled={saving || player.role === 'dev'}
                              onClick={() => void deactivatePlayer(player)}
                              type="button"
                            >
                              Inativar
                            </button>
                          ) : (
                            <button
                              className="button-primary h-9"
                              disabled={saving}
                              onClick={() => void reactivatePlayer(player)}
                              type="button"
                            >
                              Reativar
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Panel>
          </section>
        ) : null}

        {view === 'player' ? (
          <section className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
            <Panel title="Perfil do jogador">
              {authSession ? (
                <div className="grid gap-2 text-sm text-zinc-300">
                  <p><span className="text-zinc-500">Discord:</span> {authSession.discordName}</p>
                  <p><span className="text-zinc-500">Nick Albion:</span> {authSession.nick}</p>
                  <p><span className="text-zinc-500">Acesso:</span> {canManage ? 'Staff' : 'Membro'}</p>
                </div>
              ) : (
                <div className="grid gap-3">
                  <p className="text-sm text-zinc-400">Entre com Discord para vincular seu nick do Albion e participar dos check-ins.</p>
                  <button className="button-primary" onClick={() => void loginWithDiscord()} type="button">Entrar com Discord</button>
                </div>
              )}
            </Panel>
            <Panel title="Eventos disponiveis">
              <div className="grid gap-3">
                {events.map((event) => (
                  <div className="item-card" key={event.id}>
                    <p className="font-semibold">{event.title}</p>
                    <p className="mt-1 text-sm text-zinc-400">{event.content_type} / {formatDate(event.event_date)}</p>
                  </div>
                ))}
              </div>
            </Panel>
          </section>
        ) : null}
      </section>
    </main>
  );
}

function Metric({ label, value, compact = false }: { label: string; value: number | string; compact?: boolean }) {
  return (
    <div className={compact ? 'metric-compact' : 'surface rounded-md p-4'}>
      <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">{label}</p>
      <p className={compact ? 'mt-1 truncate text-xl font-bold text-white' : 'mt-2 truncate text-2xl font-bold text-white'}>{value}</p>
    </div>
  );
}

function BucketList({ title, rows }: { title: string; rows: Bucket[] }) {
  return (
    <div className="rounded border border-zinc-800 bg-zinc-950/60 p-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">{title}</p>
      <div className="mt-3 space-y-2">
        {rows.slice(0, 5).map((row) => (
          <div className="grid grid-cols-[1fr_auto] gap-3 text-sm" key={row.label}>
            <span className="min-w-0 truncate text-zinc-300">{row.label}</span>
            <span className="font-semibold text-red-400">{row.total}</span>
          </div>
        ))}
        {!rows.length ? <span className="text-sm text-zinc-500">Sem dados</span> : null}
      </div>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="surface rounded-md p-4">
      <h2 className="mb-4 text-base font-bold text-white">{title}</h2>
      {children}
    </section>
  );
}

function MultiSelect({
  label,
  options,
  selected,
  onChange,
  display,
}: {
  label: string;
  options: string[];
  selected: string[];
  onChange: (value: string[]) => void;
  display?: (value: string) => string;
}) {
  return (
    <div>
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">{label}</p>
      <div className="grid max-h-40 gap-2 overflow-auto rounded border border-zinc-800 bg-zinc-950 p-2">
        {options.map((option) => {
          const key = option.split(':')[0];
          const checked = selected.includes(option) || selected.includes(key);
          return (
            <label className="flex items-center gap-2 text-sm text-zinc-300" key={option}>
              <input
                checked={checked}
                onChange={(event) => {
                  if (event.target.checked) onChange([...selected, option]);
                  else onChange(selected.filter((item) => item !== option && item !== key));
                }}
                type="checkbox"
              />
              <span>{display ? display(option) : option}</span>
            </label>
          );
        })}
      </div>
    </div>
  );
}

function MountMultiSelect({
  mounts,
  selected,
  onChange,
}: {
  mounts: Mount[];
  selected: string[];
  onChange: (value: string[]) => void;
}) {
  return (
    <div>
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">Montarias permitidas</p>
      <div className="grid max-h-72 gap-2 overflow-auto rounded border border-zinc-800 bg-zinc-950 p-2">
        {mounts.map((mount) => {
          const checked = selected.includes(mount.mount_name);
          return (
            <label className="grid grid-cols-[auto_2.5rem_1fr] items-center gap-3 rounded border border-zinc-800 bg-zinc-900/50 p-2 text-sm text-zinc-300" key={mount.mount_name}>
              <input
                checked={checked}
                onChange={(event) => {
                  if (event.target.checked) onChange([...selected, mount.mount_name]);
                  else onChange(selected.filter((item) => item !== mount.mount_name));
                }}
                type="checkbox"
              />
              {mount.icon_url ? <img alt="" className="h-10 w-10 rounded bg-zinc-950 object-contain" src={mount.icon_url} /> : <span />}
              <span className="min-w-0">
                <span className="block truncate font-semibold text-zinc-100">{mountLabel(mount)}</span>
                <span className="block truncate text-xs text-zinc-500">{mountDetail(mount)}</span>
              </span>
            </label>
          );
        })}
      </div>
    </div>
  );
}
