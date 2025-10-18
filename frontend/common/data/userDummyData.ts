import UserImage from '../../assets/img/wanna/wanna1.png';
import UserImage2 from '../../assets/img/wanna/wanna2.png';
import { TColor } from '../../type/color-type';

export interface IPlan {
	type: string;
	processProgramationAvalaible: string;
	processChekingAvalaible: string;
	planExpiration: string;
	planRenewed: string;
	planStarted: string;
}

export interface IUserProps {
	id: string;
	username: string;
	name: string;
	surname: string;
	position: string;
	email?: string;
	src: string;
	isOnline: boolean;
	isReply?: boolean;
	color: TColor;
	fullImage?: string;
	password: string;
	checksCount: string; // Podrías cambiar a number si aplica
	processfinished: string;
	plan: IPlan;
}

const john: IUserProps = {
	id: '1',
	username: 'visanow',
	name: 'Visa',
	surname: 'Now',
	position: 'Empresa',
	email: 'info@visanow.com',
	src: `../../assets/img/wanna/${UserImage}`,
	isOnline: true,
	isReply: true,
	color: 'primary',
	// services: [SERVICES.SURFING, SERVICES.KITE_SURFING, SERVICES.TENNIS],
	password: '@ABC123',
};

const grace: IUserProps = {
	id: '2',
	username: 'grace',
	name: 'Grace',
	surname: 'Buckland',
	position: 'Empresa',
	email: 'grace@omtanke.studio',
	src: UserImage2,
	isOnline: true,
	color: 'warning',
	// services: [SERVICES.SNOWBOARDING, SERVICES.ICE_SKATING, SERVICES.KITE_SURFING],
	password: '@ABC123',
};

const USERS: { [key: string]: IUserProps } = {
	JOHN: john,
	GRACE: grace,
};

export function getUserDataWithUsername(username: string): IUserProps {
	// @ts-ignore
	return USERS[Object.keys(USERS).filter((f) => USERS[f].username.toString() === username)];
}

export function getUserDataWithId(id?: string): IUserProps {
	// @ts-ignore
	return USERS[Object.keys(USERS).filter((f) => USERS[f].id.toString() === id.toString())];
}

export default USERS;
